" Vim syntax file
" Language: Simio I/O Automata
" Maintainer: Jon Gjengset
" Latest Revision: 4 December 2014

if exists("b:current_syntax")
  finish
endif

syn include @Python syntax/python.vim

" Keywords
syn match Comment /^\s*#.*$/
syn match sectionKeywords /^\(Name\|Signature-\(Input\|Output\)\|Tasks\)/
syn match sectionKeywords /^Transition-Name/
syn match executableKeywords /^\(State\|\(Transition-\(Precondition\|Output\|Effect\)\)\)/ contained
syn match specialVariables /\<self\.\(i\|weights\|nbrs\|markcb\)\>/ contained
syn match specialVariables /\<\(to\|from\)\>/ contained
syn match globalVariables /\<N\>/ contained
hi def link executableKeywords Identifier
hi def link sectionKeywords Identifier
hi def link specialVariables Special
hi def link globalVariables Define

syn match connectKeyword /\<connect\>/ contained
hi def link connectKeyword Keyword

syn region sigOutRegion start=/^Signature-Output:/ end=/^\ze[^ \t]/ contains=sectionKeywords,connectKeyword,Comment
syn region stateRegion start=/^State:/ end=/^\ze[^ \t]/ contains=executableKeywords,@Python,specialVariables,globalVariables
syn region transitionRegion start=/^Transition-\(Precondition\|Output\|Effect\):/ end=/^\ze[^ \t]/ contains=executableKeywords,@Python,specialVariables,globalVariables

let b:current_syntax = "simio"
