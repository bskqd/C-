<template>
  <b-card header-tag="header">
    <div class="flex-row-sb text-left">
      <div class="col-6">
        <label class="text-bold-600">
          {{ $t('number') }}:
        </label>
        <b-input
          v-model="number"
          @blur="$v.number.$touch()"
          :placeholder="$t('number')"
          type="number"
        />
        <ValidationAlert
          v-if="$v.number.$dirty && !$v.number.required"
          :text="$t('emptyField')"
        />
      </div>
      <div class="col-6">
        <label class="text-bold-600">
          {{ $t('dateIssue') }}:
        </label>
        <b-input-group>
          <b-form-input
            v-model="dateIssued"
            @blur="$v.dateIssueObject.$touch()"
            type="date"
          />
          <b-input-group-append>
            <b-form-datepicker
              v-model="dateIssued"
              @hidden="$v.dateIssueObject.$touch()"
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
          v-if="$v.dateIssueObject.$dirty && !$v.dateIssueObject.required"
          :text="$t('emptyField')"
        />
        <ValidationAlert
          v-else-if="$v.dateIssueObject.$dirty && (!$v.dateIssueObject.maxValue || !$v.dateIssueObject.minValue)"
          :text="$t('dateIssuedValid')"
        />
      </div>
    </div>

    <div class="flex-row-sb text-left mt-2">
      <div class="col-12">
        <label class="text-bold-600">
          {{ $t('wayBillNumber') }}:
        </label>
        <b-input
          v-model="waybillNumber"
          :placeholder="$t('number')"
          type="number"
        />
      </div>
    </div>

    <div class="flex-row-sb mt-2">
      <div class="col-12 text-left">
        <label class="text-bold-600">
          {{ $t('affiliate') }}:
        </label>
        <multiselect
          v-model="branchOffice"
          :options="mappingAffiliate"
          :allow-empty="false"
          :searchable="true"
          :placeholder="$t('affiliate')"
          :label="labelName"
          track-by="id"
        />
      </div>
    </div>

    <div class="flex-row-sb mt-2">
      <div class="col-12 text-left">
        <label class="text-bold-600">
          {{ $t('nameUK') }}:
        </label>
        <b-input
          v-model="agentNameUkr"
          @blur="$v.agentNameUkr.$touch()"
          :placeholder="$t('nameUK')"
          type="text"
        />
        <ValidationAlert
          v-if="$v.agentNameUkr.$dirty && !$v.agentNameUkr.required"
          :text="$t('emptyField')"
        />
        <ValidationAlert
          v-else-if="$v.agentNameUkr.$dirty && !$v.agentNameUkr.alphaUA"
          :text="$t('noAlphaUA')"
        />
      </div>
    </div>

    <div class="flex-row-sb mt-2">
      <div class="col-12 text-left">
        <label class="text-bold-600">
          {{ $t('nameEN') }}:
        </label>
        <b-input
          v-model="agentNameEng"
          @blur="$v.agentNameEng.$touch()"
          :placeholder="$t('nameEN')"
          type="text"
        />
        <ValidationAlert
          v-if="$v.agentNameEng.$dirty && !$v.agentNameEng.required"
          :text="$t('emptyField')"
        />
        <ValidationAlert
          v-else-if="$v.agentNameEng.$dirty && !$v.agentNameEng.alphaEN"
          :text="$t('noAlpha')"
        />
      </div>
    </div>

    <div class="flex-row-sb text-left mt-2">
      <div class="col-12">
        <label class="text-bold-600">
          {{ $t('strictBlank') }}:
        </label>
        <b-input
          v-model="strictBlank"
          :placeholder="$t('number')"
          type="number"
        />
      </div>
    </div>

    <div>
      <FileDropZone ref="mediaContent" class="w-100 p-0 mt-1" />
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
        @click="checkSaveEditRecord()"
        variant="success"
        class="mt-2"
      >
        {{ $t('save') }}
      </b-button>
    </b-overlay>
  </b-card>
</template>

<script src="./SailorRecordBookEdit.js"/>
