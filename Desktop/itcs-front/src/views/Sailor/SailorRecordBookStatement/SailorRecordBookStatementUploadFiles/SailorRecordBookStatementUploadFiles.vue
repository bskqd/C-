<template>
  <b-card header-tag="header">
    <FileDropZone ref="mediaContent" class="w-100 mt-1" />
    <b-overlay
      :show="buttonLoader"
      spinner-variant="primary"
      opacity="0.65"
      blur="2px"
      variant="white"
      class="w-100 mt-1"
      spinner-small
    >
      <b-button
        @click="uploadFile()"
        variant="success"
        class="mt-3"
      >
        {{ $t('save') }}
      </b-button>
    </b-overlay>
  </b-card>
</template>

<script src="./SailorRecordBookStatementUploadFiles.js"/>
