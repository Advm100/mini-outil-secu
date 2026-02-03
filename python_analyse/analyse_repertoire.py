
#!/bin/bash
CHECKLIST="./checklist.txt"
LOG="$HOME/audit_fichiers.log"
FIX=0

log_issue(){ echo "[$(date '+%F %T')] $1 | actuel:$2 | attendu:$3" >>"$LOG"; }

check_file(){
  f="$1"; pe="$2"; ue="$3"; ge="$4"; ie="$5"
  [ ! -e "$f" ] && log_issue "$f inexistant" "n/a" "existe" && return
  pc=$(stat -c "%a" "$f"); uc=$(stat -c "%U" "$f"); gc=$(stat -c "%G" "$f")
  at=$(lsattr "$f" 2>/dev/null | awk '{print $1}')
  [ "$pc" != "$pe" ] && log_issue "$f perm_ko" "$pc" "$pe" && [ $FIX -eq 1 ] && chmod "$pe" "$f"
  [ "$uc" != "$ue" ] || [ "$gc" != "$ge" ] && log_issue "$f owner_ko" "$uc:$gc" "$ue:$ge" && [ $FIX -eq 1 ] && chown "$ue:$ge" "$f"
  echo "$at" | grep -q "i" && has_i=1 || has_i=0
  [ "$ie" = "yes" ] && [ $has_i -eq 0 ] && log_issue "$f immu_absente" "$at" "i" && [ $FIX -eq 1 ] && chattr +i "$f"
  [ "$ie" = "no"  ] && [ $has_i -eq 1 ] && log_issue "$f immu_inattendue" "$at" "sans i" && [ $FIX -eq 1 ] && chattr -i "$f"
}

check_passwd(){
  [ ! -f /etc/passwd ] && return
  while IFS=: read -r u p _; do
    [ -z "$u" ] && continue
    [ "$p" != "x" ] && log_issue "/etc/passwd contenu_ko" "user=$u,pass=$p" "pass=x"
  done </etc/passwd
}

main(){
  [ "$1" = "-f" ] || [ "$1" = "--fix" ] && FIX=1
  touch "$LOG" || { echo "Log inaccessible: $LOG"; exit 1; }
  while IFS=';' read -r f pe ue ge ie; do
    [[ -z "$f" || "$f" =~ ^# ]] && continue
    check_file "$f" "$pe" "$ue" "$ge" "$ie"
  done <"$CHECKLIST"
  check_passwd
}

main "$@"