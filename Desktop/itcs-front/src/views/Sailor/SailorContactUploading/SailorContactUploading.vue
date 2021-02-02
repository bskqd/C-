<template>
  <b-card class="p-2" no-body>
    <div v-if="statementAlreadyExist">
      {{ $t('statementIsPending') }}
    </div>
    <div v-else>
      <div class="position-relative">
        <FileDropZone ref="mediaContent" />
        <ValidationAlert
          v-if="$v.mediaFilesArray.$dirty && !$v.mediaFilesArray.required"
          :text="$t('emptyField')"
        />
      </div>
      <b-overlay
        :show="buttonLoader"
        spinner-variant="primary"
        opacity="0.65"
        blur="2px"
        variant="white"
        spinner-small
      >
        <b-button
          @click="validationCheck"
          class="mt-1"
          type="submit"
          variant="success"
        >
          {{ $t('save') }}
        </b-button>
      </b-overlay>
    </div>
  </b-card>
</template>

<script src="./SailorContactUploading.js" />
