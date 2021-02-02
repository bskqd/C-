<template>
  <b-card v-if="Object.keys(sailorDocument).length" header-tag="header">
    <template #header>
      <div class="flex-row-sb">
        <div class="text-uppercase text-left">
          {{ $t(`${Object.keys(sailorDocument.behavior)[0]}-${type}`) }}
          <span v-if="checkAccess('backOffice')">
            (ID: {{ sailorDocument.id }})
          </span>
        </div>
        <div class="documentIconControl">
          <unicon
            @click="viewDetailedComponent(sailorDocument, 'viewInfoBlock')"
            fill="#42627e"
            height="25px"
            width="25px"
            class="cursor mr-4"
            name="info-circle"
          />
          <unicon
            v-if="checkAccess(type, 'edit', sailorDocument)"
            @click="viewDetailedComponent(sailorDocument, 'viewEditBlock')"
            name="pen"
            fill="#42627e"
            height="25px"
            width="25px"
            class="cursor mr-4"
          />
          <unicon
            v-if="checkAccess(type, 'transfer', sailorDocument)"
            @click="viewDetailedComponent(sailorDocument, 'viewTransferBlock')"
            name="file-upload-alt"
            fill="#42627e"
            height="25px"
            width="25px"
            class="cursor mr-4"
          />
          <unicon
            v-if="checkAccess(type, 'files', sailorDocument)"
            @click="viewDetailedComponent(sailorDocument, 'viewFilesBlock')"
            name="scenery"
            fill="#42627e"
            height="25px"
            width="25px"
            class="cursor mr-4"
          />
          <unicon
            v-if="checkAccess(type, 'delete', sailorDocument)"
            @click="deleteDocument"
            name="trash-alt"
            fill="#42627e"
            height="25px"
            width="25px"
            class="cursor mr-4"
          />
          <unicon
            @click="back('experience-statements')"
            name="multiply"
            fill="#42627e"
            height="25px"
            width="25px"
            class="close"
          />
        </div>
      </div>
    </template>
    <SailorRecordBookStatementInfo
      v-if="sailorDocument.behavior.viewInfoBlock"
      :sailorDocument="sailorDocument"/>

    <SailorRecordBookStatementEdit
      v-else-if="sailorDocument.behavior.viewEditBlock"
      :sailorDocument="sailorDocument"/>

    <SailorRecordBookStatementUploadFiles
      v-else-if="sailorDocument.behavior.viewTransferBlock"
      :sailorDocument="sailorDocument"/>

    <ViewPhotoList
      v-else-if="sailorDocument.behavior.viewFilesBlock"
      :sailorDocument="sailorDocument"
      :documentType="type"/>
  </b-card>
</template>

<script src="./SailorRecordBookStatementDocument.js" />
