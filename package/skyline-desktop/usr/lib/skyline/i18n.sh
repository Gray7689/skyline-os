# SkyLine translations for shell tools. Source it, then:
#   t "English text"                 prints it in the desktop's language
#   tf "SkyLine %s is ready" "$v"    the same, with printf-style %s values
# The words live in /usr/share/skyline/l10n/<lang>.json (see skyline_i18n.py).

SKYLINE_LANG=${SKYLINE_LANG:-$(python3 "${SKYLINE_LIB:-/usr/lib/skyline}/skyline_i18n.py" --lang 2>/dev/null || echo en)}
export SKYLINE_LANG

t() {
	if [ "$SKYLINE_LANG" = en ]; then
		printf '%s' "$1"
	else
		python3 "${SKYLINE_LIB:-/usr/lib/skyline}/skyline_i18n.py" "$1" 2>/dev/null || printf '%s' "$1"
	fi
}

tf() {
	local fmt
	fmt=$(t "$1")
	shift
	# shellcheck disable=SC2059
	printf "$fmt" "$@"
}
