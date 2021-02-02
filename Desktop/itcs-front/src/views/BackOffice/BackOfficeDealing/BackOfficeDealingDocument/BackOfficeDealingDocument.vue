<template>
  <b-card v-if="Object.keys(sailorDocument).length" header-tag="header">
    <template #header>
      <div class="flex-row-sb">
        <div class="text-uppercase text-left">
          {{ $t(`${Object.keys(sailorDocument.behavior)[0]}-${type}`, { course: sailorDocument[labelName] }) }}
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
            @click="back('dealing-backoffice')"
            name="multiply"
            fill="#42627e"
            height="25px"
            width="25px"
            class="close"
          />
        </div>
      </div>
    </template>
    <BackOfficeDealingInfo
      v-if="sailorDocument.behavior.viewInfoBlock"
      :sailorDocument="sailorDocument"/>

    <BackOfficeDealingEdit
      v-else-if="sailorDocument.behavior.viewEditBlock"
      :sailorDocument="sailorDocument"/>
  </b-card>
</template>

<script src="./BackOfficeDealingDocument.js" />
