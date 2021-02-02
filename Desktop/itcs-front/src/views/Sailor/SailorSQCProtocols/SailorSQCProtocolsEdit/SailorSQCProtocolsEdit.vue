<template>
  <b-card header-tag="header">
    <div class="text-left d-flex flex-wrap">
      <div class="w-100">
        <label>
          {{ $t('number') }}:
          <span class="requaredFieldStar">*</span>
        </label>
        <b-input
          v-model="sailorDocument.number"
          @blur="$v.sailorDocument.number.$touch()"
          :placeholder="$t('number')"
          type="number"
        />
        <ValidationAlert
          v-if="$v.sailorDocument.number.$dirty && !$v.sailorDocument.number.required"
          :text="$t('emptyField')"
        />
      </div>

      <div class="w-50 mt-2">
        <label>
          {{ $t('headCommission') }}
          <span class="requaredFieldStar">*</span>
        </label>
        <multiselect
          v-model="sailorDocument.headCommission"
          @close="$v.sailorDocument.headCommission.$touch()"
          :options="commissionMembers"
          :searchable="true"
          :placeholder="$t('headCommission')"
          label="user_fio_ukr"
          track-by="signer"
        />
        <ValidationAlert
          v-if="$v.sailorDocument.headCommission.$dirty && !$v.sailorDocument.headCommission.required"
          :text="$t('emptyField')"
        />
      </div>

      <div class="w-50 mt-2">
        <label>
          {{ $t('secretaryCommission') }}
          <span class="requaredFieldStar">*</span>
        </label>
        <multiselect
          v-model="sailorDocument.secretaryCommission"
          @close="$v.sailorDocument.secretaryCommission.$touch()"
          :options="commissionMembers"
          :searchable="true"
          :placeholder="$t('secretaryCommission')"
          label="user_fio_ukr"
          track-by="signer"
        />
        <ValidationAlert
          v-if="$v.sailorDocument.secretaryCommission.$dirty && !$v.sailorDocument.secretaryCommission.required"
          :text="$t('emptyField')"
        />
      </div>

      <div class="w-100 mt-2">
        <label>
          {{ $t('membersCommission') }}
          <span class="requaredFieldStar">*</span>
        </label>
        <multiselect
          v-model="sailorDocument.membersCommission"
          @close="$v.sailorDocument.membersCommission.$touch()"
          :options="commissionMembers"
          :searchable="true"
          :multiple="true"
          :placeholder="$t('membersCommission')"
          label="user_fio_ukr"
          track-by="signer"
        />
        <ValidationAlert
          v-if="$v.sailorDocument.membersCommission.length.$dirty && (!$v.sailorDocument.membersCommission.length.minValue ||
           !$v.sailorDocument.membersCommission.length.maxValue)"
          :text="$t('invalidCommissionCount')"
        />
<!--        <ValidationAlert-->
<!--          v-else-if="$v.sailorDocument.membersCommission.$dirty && (!$v.sailorDocument.membersCommission.length.minValue ||-->
<!--             !$v.dataForm.membersCommission.length.maxValue)"-->
<!--          :text="$t('invalidCommissionCount')"-->
<!--        />-->
      </div>
    </div>
    <div>
      <b-overlay
        :show="buttonLoader"
        spinner-variant="primary"
        opacity="0.65"
        blur="2px"
        variant="white"
        class="w-100 mt-2"
        spinner-small
      >
        <b-button
          @click="checkEditedProtocol()"
          variant="success"
        >
          {{ $t('save') }}
        </b-button>
      </b-overlay>
    </div>
  </b-card>
</template>

<script src="./SailorSQCProtocolsEdit.js" />
