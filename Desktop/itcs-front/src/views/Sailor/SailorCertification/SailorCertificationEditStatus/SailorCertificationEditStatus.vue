<template>
  <b-card header-tag="header">
    <div class="seafarerInfoList">
      <div class="col-12">
        <b>{{ $t('status') }}:</b>
        <multiselect
          v-model="status"
          :options="mappingStatuses"
          :searchable="true"
          :placeholder="$t('status')"
          :allow-empty="false"
          :label="labelName"
          track-by="id"
        />
      </div>
      <div class="text-center w-full">
        <b-button
          @click="saveStatus()"
          variant="success"
          class="w-25"
          style="margin-bottom: 0px!important"
        >
          {{ $t('save') }}
        </b-button>
      </div>
    </div>
  </b-card>
</template>

<script src="./SailorCertificationEditStatus.js"/>
