<template>
  <b-card v-if="Object.keys(sailorDocument).length" header-tag="header">
    <template #header>
      <div class="flex-row-sb">
        <div class="text-uppercase text-left">
          {{ $t(`view-${type}`) }}
          <span v-if="checkAccess('backOffice')">
            (ID: {{ sailorDocument.id }})
          </span>
        </div>
        <div class="documentIconControl">
          <unicon
            v-if="checkAccess(type, 'update', sailorDocument)"
            @click="updateWishList"
            name="sync"
            fill="#42627e"
            height="25px"
            width="25px"
            class="cursor mr-4"
          />

          <unicon
            v-if="checkAccess(type, 'transfer', sailorDocument)"
            @click="moveToApplicationSQC"
            name="file-upload-alt"
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
            @click="back('sqc-wishes')"
            name="multiply"
            fill="#42627e"
            height="25px"
            width="25px"
            class="close"
          />
        </div>
      </div>
    </template>
    <SailorSQCWishesInfo :sailorDocument="sailorDocument"/>
  </b-card>
</template>

<script src="./SailorSQCWishesDocument.js" />
