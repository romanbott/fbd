#!/usr/bin/env node
'use strict';

// drawio-render: renderiza archivos .drawio a PNG o SVG usando Puppeteer y el
// modo embed de draw.io. Es una herramienta genérica: funciona sobre cualquier
// carpeta y puede usarse como CLI o como módulo.
//
// Uso:  drawio-render [inputDir] [opciones]
//       drawio-render --help

const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer');

const pkg = require('./package.json');

const DEFAULT_EMBED_URL = process.env.DRAWIO_EMBED_URL || 'https://embed.diagrams.net';
const EMBED_PARAMS = 'embed=1&proto=json&spin=1';
const FORMATS = ['png', 'svg'];

const DEFAULTS = {
  out: null,
  scale: 3,
  border: 10,
  background: '#ffffff',
  format: 'png',
  recursive: false,
  backupDir: null,
  backup: true,
  embedUrl: DEFAULT_EMBED_URL,
  timeout: 45000,
  dryRun: false,
};

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function embedUrl(base) {
  const sep = base.includes('?') ? '&' : '?';
  return base + sep + EMBED_PARAMS;
}

async function waitForMsg(page, predicate, timeout) {
  const start = Date.now();
  while (Date.now() - start < timeout) {
    const msgs = await page.evaluate(() => window.__msgs || []);
    const found = msgs.find(predicate);
    if (found) return found;
    await sleep(100);
  }
  throw new Error('Timeout esperando mensaje de draw.io');
}

async function send(page, msg) {
  await page.evaluate((m) => {
    const frame = document.getElementById('d');
    frame.contentWindow.postMessage(JSON.stringify(m), '*');
  }, msg);
}

function hostHtml(url) {
  return (
    '<!DOCTYPE html><html><head><script>' +
    'window.__msgs=[];' +
    'window.addEventListener("message",function(e){try{' +
    'window.__msgs.push(JSON.parse(e.data));}catch(_){}});' +
    '</script></head><body style="margin:0">' +
    '<iframe id="d" style="border:0;width:1200px;height:1200px" src="' +
    url +
    '"></iframe></body></html>'
  );
}

function decodeExport(dataUrl) {
  const comma = dataUrl.indexOf(',');
  const header = dataUrl.slice(0, comma);
  const payload = dataUrl.slice(comma + 1);
  if (/;base64/i.test(header)) return Buffer.from(payload, 'base64');
  return Buffer.from(decodeURIComponent(payload), 'utf8');
}

// Renderiza un único diagrama. `opts` acepta: format, scale, border,
// background, embedUrl y timeout. Devuelve el tamaño (bytes) del archivo.
async function renderDrawio(browser, xml, outPath, opts) {
  const page = await browser.newPage();
  try {
    await page.setViewport({ width: 1200, height: 1200 });
    await page.setContent(hostHtml(embedUrl(opts.embedUrl)), { waitUntil: 'domcontentloaded' });

    await page.evaluate(() => { window.__msgs = []; });
    await waitForMsg(page, (m) => m.event === 'init', opts.timeout);
    await page.evaluate(() => { window.__msgs = []; });

    await send(page, { action: 'load', xml });
    await waitForMsg(page, (m) => m.event === 'load', opts.timeout);

    await send(page, {
      action: 'export',
      format: opts.format,
      scale: opts.scale,
      border: opts.border,
      background: opts.background,
      size: 'diagram',
    });

    const exp = await waitForMsg(
      page,
      (m) => m.event === 'export' && typeof m.data === 'string' && m.data.startsWith('data:image/'),
      opts.timeout
    );

    const buf = decodeExport(exp.data);
    fs.mkdirSync(path.dirname(outPath), { recursive: true });
    fs.writeFileSync(outPath, buf);
    return buf.length;
  } finally {
    await page.close();
  }
}

// Recorre `dir` y devuelve los .drawio encontrados como { abs, rel }.
function findDrawios(dir, recursive) {
  const found = [];
  const walk = (current, rel) => {
    for (const entry of fs.readdirSync(current, { withFileTypes: true })) {
      if (entry.name.startsWith('.')) continue;
      const abs = path.join(current, entry.name);
      const childRel = rel ? path.join(rel, entry.name) : entry.name;
      if (entry.isDirectory()) {
        if (recursive) walk(abs, childRel);
      } else if (entry.name.toLowerCase().endsWith('.drawio')) {
        found.push({ abs, rel: childRel });
      }
    }
  };
  walk(dir, '');
  found.sort((a, b) => a.rel.localeCompare(b.rel));
  return found;
}

async function renderDirectory(opts) {
  const inputArg = path.resolve(opts.input || '.');
  const stat = fs.existsSync(inputArg) ? fs.statSync(inputArg) : null;
  const isFile = !!(stat && stat.isFile());

  let inputDir;
  let files;
  if (isFile) {
    if (!inputArg.toLowerCase().endsWith('.drawio')) {
      throw new Error('El archivo de entrada no es .drawio: ' + inputArg);
    }
    inputDir = path.dirname(inputArg);
    files = [{ abs: inputArg, rel: path.basename(inputArg) }];
  } else if (stat && stat.isDirectory()) {
    inputDir = inputArg;
    files = findDrawios(inputDir, opts.recursive);
  } else {
    throw new Error('No existe el archivo o directorio de entrada: ' + inputArg);
  }

  const outDir = path.resolve(opts.out || inputDir);
  const backupDir = path.resolve(opts.backupDir || path.join(outDir, 'original'));

  if (files.length === 0) {
    console.error('No hay archivos .drawio en ' + inputDir);
    return { ok: false, total: 0, failed: 0 };
  }

  const jobs = files.map((f) => {
    const base = f.rel.replace(/\.drawio$/i, '');
    return { abs: f.abs, rel: f.rel, out: path.join(outDir, base + '.' + opts.format) };
  });

  console.log('Entrada  : ' + (isFile ? inputArg : inputDir));
  console.log('Salida   : ' + outDir);
  console.log('Formato  : ' + opts.format + ' (scale=' + opts.scale + ', border=' + opts.border + ', fondo=' + opts.background + ')');
  console.log('Archivos : ' + jobs.length + (!isFile && opts.recursive ? ' (recursivo)' : ''));
  console.log('');

  if (opts.dryRun) {
    for (const j of jobs) {
      console.log('  [dry-run] ' + j.rel + ' -> ' + path.relative(process.cwd(), j.out));
    }
    console.log('\n(dry-run: no se escribió nada)');
    return { ok: true, total: jobs.length, failed: 0 };
  }

  if (opts.backup) {
    let moved = 0;
    for (const j of jobs) {
      if (!fs.existsSync(j.out)) continue;
      const dst = path.join(backupDir, path.relative(outDir, j.out));
      if (fs.existsSync(dst)) continue;
      fs.mkdirSync(path.dirname(dst), { recursive: true });
      fs.renameSync(j.out, dst);
      moved++;
    }
    if (moved) console.log('Respaldados ' + moved + ' archivo(s) en ' + path.relative(process.cwd(), backupDir) + '\n');
  }

  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu', '--disable-dev-shm-usage'],
  });

  let failed = 0;
  const results = [];
  try {
    for (const j of jobs) {
      const xml = fs.readFileSync(j.abs, 'utf8');
      process.stdout.write('Renderizando ' + j.rel + ' ... ');
      try {
        const size = await renderDrawio(browser, xml, j.out, opts);
        console.log('OK (' + size + ' bytes)');
        results.push([path.relative(outDir, j.out) || path.basename(j.out), size]);
      } catch (e) {
        console.log('FALLO: ' + e.message);
        failed++;
      }
    }
  } finally {
    await browser.close();
  }

  console.log('\nResumen:');
  for (const [f, s] of results) console.log('  ' + f + '  ' + s + ' bytes');
  if (failed) console.error('\n' + failed + ' diagrama(s) fallaron.');
  else console.log('\nListo.');

  return { ok: failed === 0, total: jobs.length, failed };
}

function parseArgs(argv) {
  const opts = { ...DEFAULTS };
  let input = null;
  const args = argv.slice();

  for (let i = 0; i < args.length; i++) {
    let flag = args[i];
    let inline = null;
    if (flag.startsWith('--')) {
      const eq = flag.indexOf('=');
      if (eq !== -1) {
        inline = flag.slice(eq + 1);
        flag = flag.slice(0, eq);
      }
    }
    const value = () => {
      if (inline !== null) return inline;
      if (i + 1 >= args.length) throw new Error('Falta el valor de ' + flag);
      return args[++i];
    };

    switch (flag) {
      case '-o': case '--out': opts.out = value(); break;
      case '-s': case '--scale': opts.scale = Number(value()); break;
      case '-b': case '--border': opts.border = Number(value()); break;
      case '--background': opts.background = value(); break;
      case '-f': case '--format': opts.format = value().toLowerCase(); break;
      case '-r': case '--recursive': opts.recursive = true; break;
      case '--backup-dir': opts.backupDir = value(); break;
      case '--no-backup': opts.backup = false; break;
      case '--embed-url': opts.embedUrl = value(); break;
      case '--timeout': opts.timeout = Number(value()); break;
      case '--dry-run': opts.dryRun = true; break;
      case '-h': case '--help': opts.help = true; break;
      case '-V': case '--version': opts.version = true; break;
      default:
        if (flag.startsWith('-')) throw new Error('Opción desconocida: ' + flag);
        if (input === null) input = flag;
        else throw new Error('Argumento inesperado: ' + flag);
    }
  }

  opts.input = input || '.';

  if (!FORMATS.includes(opts.format)) {
    throw new Error('Formato inválido: ' + opts.format + ' (usa png o svg)');
  }
  for (const key of ['scale', 'border', 'timeout']) {
    if (!Number.isFinite(opts[key]) || opts[key] <= 0) {
      throw new Error('Valor inválido para ' + key + ': ' + opts[key]);
    }
  }

  return opts;
}

function printHelp() {
  console.log(`drawio-render ${pkg.version} — renderiza .drawio a PNG/SVG

Uso:
  drawio-render [inputDir] [opciones]

Argumentos:
  inputDir                Archivo .drawio o carpeta con archivos .drawio
                          (por defecto: .)

Opciones:
  -o, --out <dir>         Carpeta de salida (por defecto: la de entrada)
  -s, --scale <n>         Escala de exportación (por defecto: 3)
  -b, --border <n>        Borde en px (por defecto: 10)
      --background <c>    Fondo, p. ej. #ffffff o transparent (por defecto: #ffffff)
  -f, --format <png|svg>  Formato de salida (por defecto: png)
  -r, --recursive         Recorre subcarpetas (replica el árbol en la salida)
      --backup-dir <dir>  Dónde respaldar salidas existentes (por defecto: <out>/original)
      --no-backup         Sobrescribe sin respaldar
      --embed-url <url>   Endpoint embed de draw.io (defecto: $DRAWIO_EMBED_URL o
                          https://embed.diagrams.net)
      --timeout <ms>      Tiempo máximo por diagrama (por defecto: 45000)
      --dry-run           Muestra lo que haría sin escribir nada
  -h, --help              Muestra esta ayuda
  -V, --version           Muestra la versión

Ejemplos:
  drawio-render ./Figuras
  drawio-render ./Figuras/3b.drawio
  drawio-render ./diagramas -r -f svg -o build
  drawio-render ./Figuras --scale 4 --background transparent
  drawio-render ./Figuras --dry-run`);
}

async function main() {
  let opts;
  try {
    opts = parseArgs(process.argv.slice(2));
  } catch (e) {
    console.error('Error: ' + e.message + '\n');
    printHelp();
    process.exit(2);
  }

  if (opts.help) { printHelp(); return; }
  if (opts.version) { console.log(pkg.version); return; }

  try {
    const result = await renderDirectory(opts);
    if (!result.ok) process.exit(1);
  } catch (e) {
    console.error('Error: ' + e.message);
    process.exit(1);
  }
}

if (require.main === module) main();

module.exports = { renderDrawio, renderDirectory, findDrawios, parseArgs };
