<template>
  <b-card header-tag="header">
    <div class="seafarerInfoList">
      <div class="w-100 pl-1 pr-1">
        <label>
          {{ $t('agentGroup') }}:
        </label>
        <multiselect
          v-model="agentGroup"
          :options="agentGroups"
          :placeholder="$t('agentGroup')"
          :preselect-first="true"
          :allow-empty="false"
          :searchable="true"
          label="name_ukr"
          track-by="id"
        />
      </div>
      <div class="w-100 pl-1 pr-1">
        <label>
          {{ $t('status') }}:
        </label>
        <multiselect
          v-model="status"
          :options="mappingStatuses"
          :placeholder="$t('status')"
          :allow-empty="false"
          :searchable="true"
          :label="labelName"
          track-by="id"
        />
      </div>
      <b-overlay
        :show="buttonLoader"
        spinner-variant="primary"
        opacity="0.65"
        blur="2px"
        variant="white"
        class="w-100 text-center"
        spinner-small
      >
        <b-button
          @click="saveAgentApplicationStatus"
          variant="success"
        >
          {{ $t('save') }}
        </b-button>
      </b-overlay>
    </div>
  </b-card>
</template>

<script src="./NewAgentsEditStatus.js" />
