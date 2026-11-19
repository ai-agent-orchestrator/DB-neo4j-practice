import {cpSync,mkdirSync,copyFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const target=path.join(root,'public/runtime');
mkdirSync(target,{recursive:true});
cpSync(path.join(root,'node_modules/@litert-lm/core/wasm'),target,{recursive:true});
copyFileSync(path.join(root,'node_modules/@litert-lm/core/package.json'),path.join(target,'package-info.json'));
console.log('Prepared pinned LiteRT-LM browser runtime');
