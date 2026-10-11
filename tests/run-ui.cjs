// Run the existing browser checks against a temporary production preview.
const { spawn } = require('node:child_process');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const port = process.env.IBT2_UI_PORT || '8081';
const url = `http://127.0.0.1:${port}`;
const server = spawn(process.execPath, [
    path.join(root, 'node_modules/vite/bin/vite.js'),
    'preview', '--host', '127.0.0.1', '--port', port, '--strictPort',
], { cwd: root, stdio: 'inherit' });
let exited = false;
server.on('exit', () => { exited = true; });
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));

(async () => {
    try {
        const deadline = Date.now() + 30000;
        while (true) {
            if (exited) throw new Error('Vite preview exited before becoming ready');
            try {
                const response = await fetch(url, { signal: AbortSignal.timeout(1000) });
                if (response.ok) break;
            } catch (_) { /* Retry until the preview is ready. */ }
            if (Date.now() >= deadline) throw new Error('Vite preview did not become ready');
            await sleep(200);
        }
        const test = spawn(process.execPath, ['tests/ui-smoke.cjs'], {
            cwd: root, stdio: 'inherit', env: { ...process.env, IBT2_UI_URL: url },
        });
        process.exitCode = await new Promise(resolve => test.on('exit', code => resolve(code ?? 1)));
    } finally {
        server.kill('SIGTERM');
    }
})().catch(error => { console.error(error); process.exitCode = 1; });
