import { createServer } from 'vite';
import { fileURLToPath } from 'url';
import path from 'path';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
process.chdir(__dirname);

async function start() {
  const server = await createServer({
    root: __dirname,
    configFile: path.join(__dirname, 'vite.config.js'),
    server: {
      port: 3000,
      host: '0.0.0.0'
    }
  });
  await server.listen();
  console.log(`[NeuroLearn Frontend] Server root: ${server.config.root}`);
  server.printUrls();
}

start().catch((err) => {
  console.error('[Vite Starter Error]:', err);
  process.exit(1);
});
