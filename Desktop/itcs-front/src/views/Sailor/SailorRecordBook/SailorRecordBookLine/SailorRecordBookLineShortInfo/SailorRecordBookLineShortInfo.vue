<template>
  <b-card header-tag="header">
    <template #header>
      <div class="flex-row-sb">
        <div class="text-uppercase">
          {{ $t(`${Object.keys(row.item.behavior)[0]}-${type}`, { page: row.item.number_page_book }) }}
          <span v-if="checkAccess('backOffice')">
            (ID: {{ row.item.id }})
          </span>
        </div>
        <unicon
          @click="hideDetailed(row)"
          name="multiply"
          fill="#42627e"
          height="20px"
          width="20px"
          class="close"
        />
      </div>
    </template>
    <SailorRecordBookLineInfo :sailorDocument="row.item"/>
    <ViewPhotoList :sailorDocument="row.item" :documentType="type"/>
  </b-card>
</template>

<script src="./SailorRecordBookLineShortInfo.js" />
