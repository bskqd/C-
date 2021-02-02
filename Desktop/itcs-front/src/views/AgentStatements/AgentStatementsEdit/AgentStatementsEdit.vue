<template>
  <b-card
    header-tag="header"
    class="pb-2"
  >
    <div class="seafarerInfoList text-left">
      <div
        v-if="sailorDocument.status_document.id === 69 || sailorDocument.status_document.id === 82 || checkAccess('admin')"
        class="w-50"
        :class="{ 'w-100 pl-1 pr-1': !(checkAccess('admin') || (checkAccess('agent') && status.id === 67) || (checkAccess('secretaryService') && !sailorDocument.date_end_proxy)) }"
      >
        <label>
          {{ $t('status') }}
          <span class="requared-field-star">*</span>
        </label>
        <multiselect
          v-model="status"
          :options="mappingStatuses"
          :placeholder="$t('status')"
          :allow-empty="false"
          :searchable="true"
          :label="langFields"
          track-by="id"
        />
      </div>

      <div
        v-if="checkAccess('admin') || (checkAccess('agent') && status.id === 67) || (checkAccess('secretaryService') && !sailorDocument.date_end_proxy)"
        class="w-50"
      >
        <label>
          {{ $t('contractDateEnd') }}
          <span class="requared-field-star">*</span>
        </label>
        <b-input-group>
          <b-form-input
            v-model="contractDateEnd"
            @blur="$v.dateEndObject.$touch()"
            type="date"
          />
          <b-input-group-append>
            <b-form-datepicker
              v-model="contractDateEnd"
              @hidden="$v.dateEndObject.$touch()"
              :locale="lang"
              min="1900-01-01"
              max="2200-01-01"
              start-weekday="1"
              button-only
              right
            />
          </b-input-group-append>
        </b-input-group>
        <ValidationAlert
          v-if="$v.dateEndObject.$dirty && !$v.dateEndObject.required"
          :text="$t('emptyField')"
        />
        <ValidationAlert
          v-else-if="$v.dateEndObject.$dirty && (!$v.dateEndObject.maxValue || !$v.dateEndObject.minValue)"
          :text="$t('invalidDataFormat')"
        />
      </div>

      <div v-if="checkAccess('admin') || sailorDocument.status_document.id === 69 || sailorDocument.status_document.id === 82">
        <FileDropZone ref="mediaContent" class="w-100" />
        <ValidationAlert
          v-if="$v.mediaFilesArray.$dirty && !$v.mediaFilesArray.required"
          :text="$t('emptyField')"
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
          @click="validationCheck"
          variant="success"
        >
          {{ $t('save') }}
        </b-button>
      </b-overlay>

    </div>
  </b-card>
</template>

<script src="./AgentStatementsEdit.js" />
