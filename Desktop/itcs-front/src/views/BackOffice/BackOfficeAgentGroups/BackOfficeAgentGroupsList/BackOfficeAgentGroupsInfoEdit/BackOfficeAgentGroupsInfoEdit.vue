<template>
  <b-card header-tag="header">
    <template #header>
      <div class="flex-row-sb">
        <div class="text-uppercase">
          {{ $t('agentInfoEdit') }}
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
    <div class="seafarerInfoList p-1">
      <label class="w-100 pl-1 pr-1 text-left">
        {{ $t('agentFullName') }}:
        <span class="requared-field-star">*</span>
      </label>
      <div class="w-33">
        <b-form-input
          v-model="lastName"
          @blur="$v.lastName.$touch"
          :placeholder="$t('lastName')"
          type="text"
        />
        <ValidationAlert
          v-if="$v.lastName.$dirty && !$v.lastName.required"
          :text="$t('emptyField')"
        />
      </div>
      <div class="w-33">
        <b-form-input
          v-model="firstName"
          @blur="$v.firstName.$touch"
          :placeholder="$t('name')"
          type="text"
        />
        <ValidationAlert
          v-if="$v.firstName.$dirty && !$v.firstName.required"
          :text="$t('emptyField')"
        />
      </div>
      <div class="w-33">
        <b-form-input
          v-model="middleName"
          @blur="$v.middleName.$touch"
          :placeholder="$t('middleName')"
          type="text"
        />
        <ValidationAlert
          v-if="$v.middleName.$dirty && !$v.middleName.required"
          :text="$t('emptyField')"
        />
      </div>
      <div
        v-if="checkAccess('backOfficeAgentGroups', 'editGroup')"
        class="w-50"
      >
        <label>
          {{ $t('agentGroup') }}:
          <span class="requared-field-star">*</span>
        </label>
        <multiselect
          v-model="agentGroup"
          :options="agentGroupsList"
          :placeholder="$t('agentGroup')"
          :searchable="true"
          :multiple="row.item.userprofile.type_user === 'secretary_service'"
          label="name_ukr"
          track-by="id"
        />
        <ValidationAlert
          v-if="$v.agentGroup.$dirty && !$v.agentGroup.required"
          :text="$t('emptyField')"
        />
      </div>
      <div :class="checkAccess('backOfficeAgentGroups', 'editGroup') ? 'w-50' : 'w-100'">
        <label>
          {{ $t('affiliate') }}:
          <span class="requared-field-star">*</span>
        </label>
        <multiselect
          v-model="affiliate"
          @close="$v.affiliate.$touch()"
          :options="affiliatesList"
          :label="labelName"
          :placeholder="$t('affiliate')"
          track-by="id"
        />
        <ValidationAlert
          v-if="$v.affiliate.$dirty && !$v.affiliate.required"
          :text="$t('emptyField')"
        />
      </div>
      <div class="w-33">
        <label>
          {{ $t('phoneNumber') }}:
          <span
            v-if="row.item.userprofile.type_user !== 'secretary_service'"
            class="requared-field-star"
          >*</span>
        </label>
        <b-form-input
          v-model="phoneNumber"
          @blur="$v.phoneNumber.$touch()"
          :placeholder="$t('phoneNumber')"
        />
        <small>{{ $t('phoneNumFormat') }}</small>
        <ValidationAlert
          v-if="$v.phoneNumber.$dirty && !$v.phoneNumber.required"
          :text="$t('emptyField')"
        />
        <ValidationAlert
          v-else-if="$v.phoneNumber.$dirty && (!$v.phoneNumber.minLength || !$v.phoneNumber.maxLength ||
           !$v.phoneNumber.phoneNumber)"
          :text="$t('invalidPhoneNum')"
        />
      </div>
      <div class="w-33">
        <label>Telegram:</label>
        <b-form-input
          v-model="telegram"
          @blur="$v.telegram.$touch()"
          placeholder="Telegram"
        />
        <small>{{ $t('phoneNumFormat') }}</small>
        <ValidationAlert
          v-if="$v.telegram.$dirty && (!$v.telegram.minLength || !$v.telegram.maxLength || !$v.telegram.phoneNumber)"
          :text="$t('invalidPhoneNum')"
        />
      </div>
      <div class="w-33">
        <label>Viber:</label>
        <b-form-input
          v-model="viber"
          @blur="$v.viber.$touch()"
          placeholder="Viber"
        />
        <small>{{ $t('phoneNumFormat') }}</small>
        <ValidationAlert
          v-if="$v.viber.$dirty && (!$v.viber.minLength || !$v.viber.maxLength || !$v.viber.phoneNumber)"
          :text="$t('invalidPhoneNum')"
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

<script src="./BackOfficeAgentGroupsInfoEdit.js" />
