_mate_completion() {
    COMPREPLY=( $( env COMP_WORDS="${COMP_WORDS[*]}" \
                   COMP_CWORD=$COMP_CWORD \
                   _MATE_COMPLETE=complete $1 ) )
    return 0
}

complete -F _mate_completion -o default mate;