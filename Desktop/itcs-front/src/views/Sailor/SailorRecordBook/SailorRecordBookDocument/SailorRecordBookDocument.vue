<template>
  <b-card v-if="Object.keys(sailorDocument).length" header-tag="header">
    <template #header>
      <div class="flex-row-sb">
        <div class="text-uppercase text-left">
          {{ $t(`${Object.keys(sailorDocument.behavior)[0]}-${type}`, { number: sailorDocument.name_book }) }}
          <span v-if="checkAccess('backOffice')">
            (ID: {{ sailorDocument.id }})
          </span>
        </div>
        <div class="documentIconControl">
          <unicon
            v-if="checkAccess(type, 'addRecord', sailorDocument)"
            @click="viewDetailedComponent(sailorDocument, 'viewAddBlock')"
            fill="#42627e"
            height="25px"
            width="25px"
            class="cursor mr-4"
            name="plus"
          />
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
            v-if="checkAccess(type, 'editStatus', sailorDocument)"
            @click="viewDetailedComponent(sailorDocument, 'viewEditStatusBlock')"
            name="sync"
            fill="#42627e"
            height="25px"
            width="25px"
            class="cursor mr-4"
          />
          <unicon
            v-if="sailorDocument.status.id === 34 && checkAccess(type, 'verificationSteps', sailorDocument)"
            @click="viewDetailedComponent(sailorDocument, 'viewVerificationStepsBlock')"
            name="folder-check"
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
            @click="$router.push({ name: 'experience-records', params: { id: id }})"
            name="multiply"
            fill="#42627e"
            height="25px"
            width="25px"
            class="close"
          />
        </div>
      </div>
    </template>
    <SailorRecordBookLineAdd
      v-if="sailorDocument.behavior.viewAddBlock"
      :sailorDocument="sailorDocument"/>

    <SailorRecordBookInfo
      v-else-if="sailorDocument.behavior.viewInfoBlock"
      :sailorDocument="sailorDocument"/>

    <SailorRecordBookEdit
      v-else-if="sailorDocument.behavior.viewEditBlock"
      :sailorDocument="sailorDocument"/>

    <SailorRecordBookEditStatus
      v-else-if="sailorDocument.behavior.viewEditStatusBlock"
      :sailorDocument="sailorDocument"/>

    <VerificationSteps
      v-else-if="sailorDocument.behavior.viewVerificationStepsBlock"
      :sailorDocument="sailorDocument"
      getFunctionName="getRecordBooks"/>

    <ViewPhotoList
      v-else-if="sailorDocument.behavior.viewFilesBlock"
      :sailorDocument="sailorDocument"
      :documentType="type"/>
  </b-card>
</template>

<script src="./SailorRecordBookDocument.js" />
