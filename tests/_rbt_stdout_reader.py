RBT_STDOUT_READER=r'''(el)=>{
 if(!el || !el.hasAttribute('data-console-copy')) throw Error('Missing data-console-copy');
 if(typeof el.dataset.consoleCopy!=='string') throw Error('Non-string data-console-copy');
 return {stdout:el.dataset.consoleCopy,stdoutDisplay:el.textContent};
}'''
