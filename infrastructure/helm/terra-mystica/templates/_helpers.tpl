{{/*
Expand the name of the chart.
*/}}
{{- define "terra-mystica.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "terra-mystica.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "terra-mystica.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "terra-mystica.labels" -}}
helm.sh/chart: {{ include "terra-mystica.chart" . }}
{{ include "terra-mystica.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "terra-mystica.selectorLabels" -}}
app.kubernetes.io/name: {{ include "terra-mystica.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Frontend labels
*/}}
{{- define "terra-mystica.frontend.labels" -}}
{{ include "terra-mystica.labels" . }}
app.kubernetes.io/component: frontend
{{- end }}

{{/*
Frontend selector labels
*/}}
{{- define "terra-mystica.frontend.selectorLabels" -}}
{{ include "terra-mystica.selectorLabels" . }}
app.kubernetes.io/component: frontend
{{- end }}

{{/*
Backend labels
*/}}
{{- define "terra-mystica.backend.labels" -}}
{{ include "terra-mystica.labels" . }}
app.kubernetes.io/component: backend
{{- end }}

{{/*
Backend selector labels
*/}}
{{- define "terra-mystica.backend.selectorLabels" -}}
{{ include "terra-mystica.selectorLabels" . }}
app.kubernetes.io/component: backend
{{- end }}

{{/*
Celery labels
*/}}
{{- define "terra-mystica.celery.labels" -}}
{{ include "terra-mystica.labels" . }}
app.kubernetes.io/component: celery
{{- end }}

{{/*
Celery selector labels
*/}}
{{- define "terra-mystica.celery.selectorLabels" -}}
{{ include "terra-mystica.selectorLabels" . }}
app.kubernetes.io/component: celery
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "terra-mystica.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "terra-mystica.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
PostgreSQL host
*/}}
{{- define "terra-mystica.postgresql.host" -}}
{{- if .Values.postgresql.enabled }}
{{- printf "%s-postgresql" (include "terra-mystica.fullname" .) }}
{{- else }}
{{- .Values.postgresql.external.host }}
{{- end }}
{{- end }}

{{/*
Redis host
*/}}
{{- define "terra-mystica.redis.host" -}}
{{- if .Values.redis.enabled }}
{{- printf "%s-redis-master" (include "terra-mystica.fullname" .) }}
{{- else }}
{{- .Values.redis.external.host }}
{{- end }}
{{- end }}

{{/*
Database URL
*/}}
{{- define "terra-mystica.database.url" -}}
{{- if .Values.postgresql.enabled }}
{{- printf "postgresql://%s:%s@%s:5432/%s" .Values.postgresql.auth.username .Values.postgresql.auth.password (include "terra-mystica.postgresql.host" .) .Values.postgresql.auth.database }}
{{- else }}
{{- .Values.backend.env.DATABASE_URL }}
{{- end }}
{{- end }}

{{/*
Redis URL
*/}}
{{- define "terra-mystica.redis.url" -}}
{{- if .Values.redis.enabled }}
{{- printf "redis://%s:6379/0" (include "terra-mystica.redis.host" .) }}
{{- else }}
{{- .Values.backend.env.REDIS_URL }}
{{- end }}
{{- end }}