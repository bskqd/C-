<template>
  <b-form @submit.prevent="checkInfo">
    <div class="text-left form-group pb-0">
      <div class="col-12">
        <label>
          {{ $t('deliveryType') }}:
        </label>
        <multiselect
          v-model="dataForm.deliveryType"
          :options="dataForm.deliveryTypeList"
          :searchable="true"
          :preselectFirst="true"
          :placeholder="$t('deliveryType')"
          :allow-empty="false"
          :label="labelName"
          track-by="id"
        />
      </div>

      <div class="col-12 mt-1">
        <label>
          {{ $t('city') }}:
          <span class="required-field-star">*</span>
        </label>
        <multiselect
          v-model="dataForm.city"
          @input="getDeliveryInfo(dataForm.city.id)"
          @close="$v.dataForm.city.$touch()"
          :options="mappingDeliveryCities"
          :searchable="true"
          :placeholder="$t('city')"
          :allow-empty="false"
          :options-limit="4500"
          label="name_ukr"
          track-by="id"
        />
        <ValidationAlert
          v-if="$v.dataForm.city.$dirty && !$v.dataForm.city.required"
          :text="$t('emptyField')"
        />
      </div>

      <!--Show if delivery type is self-pickup-->
      <div
        v-if="dataForm.deliveryType && dataForm.deliveryType.id === 1"
        class="col-12 mt-1"
      >
        <label>
          {{ $t('department') }}:
          <span class="required-field-star">*</span>
        </label>
        <b-overlay
          :show="selectLoader"
          spinner-variant="primary"
          opacity="0.65"
          blur="2px"
          variant="white"
          class="w-100 p-0"
          spinner-small
        >
          <multiselect
            v-model="dataForm.warehouse"
            @close="$v.dataForm.warehouse.$touch()"
            :options="dataForm.deliveryWarehouses"
            :searchable="true"
            :placeholder="$t('department')"
            label="name_ukr"
            track-by="id"
          />
        </b-overlay>
        <ValidationAlert
          v-if="$v.dataForm.warehouse.$dirty && !$v.dataForm.warehouse.required"
          :text="$t('emptyField')"
        />
      </div>

      <!--Show if delivery type is courier-->
      <div
        v-if="dataForm.deliveryType && dataForm.deliveryType.id === 2"
        class="col-12 d-flex mt-1"
      >
        <div class="col-4 p-0">
          <label>
            {{ $t('street') }}:
            <span class="required-field-star">*</span>
          </label>
          <b-overlay
            :show="selectLoader"
            spinner-variant="primary"
            opacity="0.65"
            blur="2px"
            variant="white"
            class="w-100"
            spinner-small
          >
            <multiselect
              v-model="dataForm.street"
              @close="$v.dataForm.street.$touch()"
              :options="dataForm.deliveryStreets"
              :searchable="true"
              :placeholder="$t('street')"
              label="name_ukr"
              track-by="id"
            />
          </b-overlay>
          <ValidationAlert
            v-if="$v.dataForm.street.$dirty && !$v.dataForm.street.required"
            :text="$t('emptyField')"
          />
        </div>
        <div class="col-4">
          <label>
            {{ $t('house') }}:
            <span class="required-field-star">*</span>
          </label>
          <b-form-input
            v-model="dataForm.house"
            @blur="$v.dataForm.house.$touch()"
            :placeholder="$t('house')"
            type="text"
          />
          <ValidationAlert
            v-if="$v.dataForm.house.$dirty && !$v.dataForm.house.required"
            :text="$t('emptyField')"
          />
        </div>
        <div class="col-4 p-0">
          <label>
            {{ $t('flat') }}:
          </label>
          <b-form-input
            v-model="dataForm.flat"
            :placeholder="$t('flat')"
            type="text"
          />
        </div>
      </div>

      <div class="col-12 mt-1">
        <label>
          {{ $t('phoneNumber') }}:
          <span class="required-field-star">*</span>
        </label>
        <phone-mask-input
          v-model="dataForm.phoneNumber"
          @onBlur="$v.dataForm.phoneNumber.$touch()"
          :placeholder="$t('phoneNumber')"
          autoDetectCountry
          class="w-full mainInfoPhone"
        />
        <ValidationAlert
          v-if="$v.dataForm.phoneNumber.$dirty && !$v.dataForm.phoneNumber.required"
          :text="$t('emptyField')"
        />
        <ValidationAlert
          v-else-if="$v.dataForm.phoneNumber.$dirty && (!$v.dataForm.phoneNumber.maxLength || !$v.dataForm.phoneNumber.minLength)"
          :text="$t('invalidPhoneNum')"
        />
      </div>

      <div class="col-12 form-group text-left mt-2">
        <FileDropZone ref="mediaContent" />
      </div>

      <div class="col-12 p-0 text-center">
        <b-overlay
          :show="dataForm.buttonLoader"
          spinner-variant="primary"
          opacity="0.65"
          blur="2px"
          variant="white"
          class="pt-1"
          spinner-small
        >
          <b-button
            type="submit"
            variant="success"
          >
            {{ $t('save') }}
          </b-button>
        </b-overlay>
      </div>
    </div>
  </b-form>
</template>

<script src="./SailorRecordBookStatementAdd.js"/>
