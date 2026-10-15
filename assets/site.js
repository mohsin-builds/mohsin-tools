import {svg} from './icons.js';
for(const element of document.querySelectorAll('[data-icon]'))element.innerHTML=svg(element.dataset.icon,Number(element.dataset.size)||24);
const year=document.querySelector('[data-year]');if(year)year.textContent=new Date().getFullYear();
const search=document.querySelector('#tool-search');if(search){search.addEventListener('input',()=>{const q=search.value.trim().toLowerCase();let n=0;for(const card of document.querySelectorAll('[data-tool-card]')){const match=card.textContent.toLowerCase().includes(q);card.hidden=!match;if(match)n++;}const empty=document.querySelector('#empty-tools');if(empty)empty.style.display=n?'none':'block';});}

// Keyboard shortcut is intentionally inactive while editing input fields.
document.addEventListener('keydown',e=>{const field=document.querySelector('#tool-search');if(!field)return;const target=e.target;if(e.key==='/'&&!e.ctrlKey&&!e.metaKey&&!e.altKey&&!['INPUT','TEXTAREA','SELECT'].includes(target?.tagName)){e.preventDefault();field.focus();}});