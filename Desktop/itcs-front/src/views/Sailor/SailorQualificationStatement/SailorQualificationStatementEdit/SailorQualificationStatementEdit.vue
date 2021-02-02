<template>
  <b-card header-tag="header">
    <div class="seafarerInfoList">
      <div class="w-100 text-left">
        <b>{{ $t('swimPorts') }}:</b>
        <multiselect
          v-model="sailorDocument.port"
          :options="portsList"
          :allow-empty="false"
          :searchable="true"
          :placeholder="$t('swimPorts')"
          :label="langFields"
          track-by="id"
        />
      </div>

      <b-overlay
        :show="buttonLoader"
        spinner-variant="primary"
        opacity="0.65"
        blur="2px"
        variant="white"
        class="w-100"
        spinner-small
      >
        <b-button
          @click="saveEditedStatement"
          variant="success"
        >
          {{ $t('save') }}
        </b-button>
      </b-overlay>
    </div>
  </b-card>
</template>

<script src="./SailorQualificationStatementEdit.js"/>
