if exists("b:current_syntax")
  finish
endif

syntax keyword nookeKeyword if elif else while do for in switch try catch finally set case default 

syntax keyword nookeKeywordSecondary continue return collect leave ignore
syntax keyword nookeProperties __scope__ __name__ __file__ __collection__ root
syntax keyword nookeCore import print stdio stderr stdin type int float boolean string

syntax match nookeIdentifierColon /\<[a-zA-Z_][a-zA-Z0-9_]*\>:/ 

syntax keyword nookeConstant true false null none 

syntax match nookeComment /#.*/

syntax match nookeFloat /\<[0-9]\+\.[0-9]\+\>/
syntax match nookeNumber /\<[0-9]\+\>/
syntax match nookeBinary /\<b[01]\+\>/
syntax match nookeHex /\<h[0-9a-fA-F]\+\>/

syntax match nookeBrace /[{}]/
syntax match nookeParen /[()]/
syntax match nookeBracket /[\[\]]/
syntax match nookeColon /:/

syntax region nookeString start=/"/ end=/"/
syntax region nookeString start=/'/ end=/'/

syntax match nookeSpread /\.\./

highlight link nookeComment Comment
highlight link nookeKeyword Keyword
highlight link nookeConstant Constant
highlight link nookeNumber Number
highlight link nookeFloat Float
highlight link nookeBinary Number
highlight link nookeHex Number
highlight link nookeString String
highlight link nookeSpread Operator

highlight nookeKeywordSecondary guifg=#1abc9c
highlight nookeProperties guifg=#A6D49F
highlight nookeCore guifg=#2ac3de

highlight nookeBrace guifg=#BB9AF7
highlight nookeBracket guifg=#e0af68
highlight nookeParen guifg=#7DCFFF
highlight nookeBrace guifg=#89DCEB

highlight nookeIdentifierColon guifg=#E0AF68 gui=bold

let b:current_syntax = "nooke"
