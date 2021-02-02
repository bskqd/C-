<template>
  <div>
    <vue-dropzone
      @vdropzone-file-added="addFile"
      @vdropzone-removed-file="removeFile"
      :options="dropzoneOptions"
      :useCustomSlot="true"
      ref="dropzone"
      id="dropzone"
    >
      <unicon
        name="upload"
        fill="#42627e"
        height="50px"
        width="50px"
      />
      <div class="m-1">
        {{ $t('dropFile') }}
      </div>
    </vue-dropzone>
  </div>
</template>

<script src="./DropZone.js" />
