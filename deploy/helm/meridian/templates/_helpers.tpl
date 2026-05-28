{{/* Common labels */}}
{{- define "meridian.labels" -}}
app.kubernetes.io/name: meridian
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
{{- end -}}

{{- define "meridian.image" -}}
{{- $reg := .registry -}}{{- $repo := .repository -}}{{- $tag := .tag -}}
{{- if $reg }}{{ $reg }}/{{ end }}{{ $repo }}:{{ $tag }}
{{- end -}}
