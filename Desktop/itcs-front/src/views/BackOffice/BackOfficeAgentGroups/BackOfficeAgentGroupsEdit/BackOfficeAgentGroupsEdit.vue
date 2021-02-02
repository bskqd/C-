<template>
  <b-card header-tag="header">
    <template #header>
      <div class="flex-row-sb">
        <div class="text-uppercase">
          {{ $t('editAgentGroup') }}
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
    <div class="seafarerInfoList">
      <div class="w-100 pl-1 pr-1">
        <label>
          {{ $t('nameUa') }}:
        </label>
        <b-form-input
          v-model="agentGroupName"
          @blur="$v.agentGroupName.$touch"
          :placeholder="$t('nameUa')"
          type="text"
        />
        <ValidationAlert
          v-if="$v.agentGroupName.$dirty && !$v.agentGroupName.required"
          :text="$t('emptyField')"
        />
      </div>
      <b-overlay
        :show="buttonLoader"
        spinner-variant="primary"
        opacity="0.65"
        blur="2px"
        variant="white"
        class="w-100"
        spinner-small
      >
        <b-button
          @click="validationCheck"
          class="mt-1"
          variant="success"
        >
          {{ $t('save') }}
        </b-button>
      </b-overlay>
    </div>
  </b-card>
</template>

<script src="./BackOfficeAgentGroupsEdit.js" />
