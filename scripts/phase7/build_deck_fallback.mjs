// Local PPTX fallback used when the live presentation renderer fails on Windows.
// Pass the workspace dependency loader's authoritative dependencies directory.
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {buildCover,buildSlides} from './build_slides.mjs';
const runtime=process.argv[2];
if(!runtime)throw new Error('Usage: bundled-node build_deck_fallback.mjs <runtime-dependencies-dir>');
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const {Presentation,PresentationFile}=await import(pathToFileURL(path.join(runtime,'node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs')).href);
const presentation=Presentation.create({slideSize:{width:1280,height:720}});
// A native session can start with a blank slide; a local model usually starts empty.
if(presentation.slides.items.length===1&&presentation.slides.getItem(0).shapes.items.length===0)presentation.slides.delete([0]);
await buildCover({presentation});
await buildSlides({presentation,input:{from:2,to:12,root}});
await fs.mkdir(path.join(root,'.phase7-build'),{recursive:true});
await(await PresentationFile.exportPptx(presentation)).save(path.join(root,'.phase7-build/agri-leaf-draft.pptx'));
console.log('Built 12 editable slides. Finalize and render the draft before delivery.');
