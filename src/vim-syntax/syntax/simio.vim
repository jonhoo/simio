" Vim syntax file
" Language: Simio I/O Automata
" Maintainer: Jon Gjengset
" Latest Revision: 4 December 2014

if exists("b:current_syntax")
  finish
endif

syn include @Python syntax/python.vim

" Keywords
syn match Comment /^#.*/
syn match sectionKeywords /^\(Name\|Signature-\(Input\|Output\)\|Tasks\)/
syn match sectionKeywords /^Transition-Name/
syn match executableKeywords /^\(State\|\(Transition-\(Precondition\|Output\|Effect\)\)\)/ contained
hi def link executableKeywords Identifier
hi def link sectionKeywords Identifier

syn region stateRegion start=/^State:/ end=/^\ze[^ \t]/ contains=executableKeywords,@Python
syn region transitionRegion start=/^Transition-\(Precondition\|Output\|Effect\):/ end=/^\ze[^ \t]/ contains=executableKeywords,@Python

let b:current_syntax = "simio"
