<template>
  <b-card header-tag="header">
    <div
      v-if="sailorDocument.is_payed"
      class="d-flex w-100 p-0 text-left"
    >
      <div class="w-50">
        <label>
          {{ $t('agent') }}:
        </label>
        <multiselect
          v-model="agent"
          @close="$v.agent.$touch()"
          :options="mappingAgents"
          :searchable="true"
          :placeholder="$t('agent')"
          :allow-empty="false"
          :label="labelName"
          track-by="id"
        />
        <ValidationAlert
          v-if="$v.agent.$dirty && !$v.agent.required"
          :text="$t('emptyField')"
        />
      </div>

      <div class="w-50">
        <label>
          {{ $t('dateIssue') }}
          <span class="required-field-star">*</span>
        </label>
        <b-input-group>
          <b-form-input
            v-model="dateStart"
            @blur="$v.dateStartObject.$touch()"
            type="date"
          />
          <b-input-group-append>
            <b-form-datepicker
              v-model="dateStart"
              @hidden="$v.dateStartObject.$touch()"
              :locale="lang"
              :max="new Date()"
              min="1900-01-01"
              start-weekday="1"
              button-only
              right
            />
          </b-input-group-append>
        </b-input-group>
        <ValidationAlert
          v-if="$v.dateStartObject.$dirty && !$v.dateStartObject.required"
          :text="$t('emptyField')"
        />
        <ValidationAlert
          v-else-if="$v.dateStartObject.$dirty && (!$v.dateStartObject.minValue || !$v.dateStartObject.maxValue)"
          :text="$t('dateIssuedValid')"
        />
      </div>
    </div>

    <div
      v-else
      class="text-left"
    >
      <div>
        <label>
          {{ $t('payment') }}:
        </label>
        <div class="align-items-center d-flex flex-row w-100 pt-1">
          <b-form-checkbox
            v-model="payment"
            name="payment"
            class="mx-1 pt-0"
            switch
          />
          <div v-if="payment">
            {{ $t('isPayed') }}
          </div>
          <div v-else>
            {{ $t('notPayed') }}
          </div>
        </div>
      </div>

      <div>
        <FileDropZone ref="mediaContent" class="w-100 p-0 mt-1" />
      </div>
    </div>

    <b-overlay
      :show="buttonLoader"
      spinner-variant="primary"
      opacity="0.65"
      blur="2px"
      variant="white"
      class="w-100 mt-3 d-flex justify-content-around"
      spinner-small
    >
      <b-button
        @click="sailorDocument.is_payed ? checkInfo() : changeApplication()"
        variant="success"
      >
        {{ $t('save') }}
      </b-button>
      <b-button
        v-if="checkAccess('recordBookStatement', 'changeStatusToRejected', sailorDocument)"
        @click="changeApplication(49)"
        variant="outline-primary"
        class="pb-2"
      >
        {{ $t('changeToReject') }}
      </b-button>
    </b-overlay>
  </b-card>
</template>

<script src="./SailorRecordBookStatementEdit.js"/>
