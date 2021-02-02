<template>
  <b-form @submit.prevent="checkInfo">
    <b-tabs fill pills>
      <b-tab
        v-if="checkAccess('serviceRecordBook', 'createNewDoc')"
        @click="checkNewRecord = true"
        :active="checkNewRecord"
      >
        <template #title>
          <div class="text-uppercase">
            {{ $t('addNew') }}
          </div>
        </template>
        <b-card-text class="text-left">
          <div class="w-100 position-relative">
            <label>
              {{ $t('agent') }}
              <span class="required-field-star">*</span>
            </label>
            <multiselect
              v-model="dataForm.newRBAgent"
              @close="$v.dataForm.newRBAgent.$touch()"
              :searchable="true"
              :options="mappingAgents"
              :placeholder="$t('agent')"
              :label="langAgent"
              track-by="id"
            />
            <ValidationAlert
              v-if="($v.dataForm.newRBAgent.$dirty && !$v.dataForm.newRBAgent.required)"
              :text="$t('emptyField')"
            />
          </div>

          <div class="d-flex">
            <div class="w-50">
              <label>
                {{ $t('strictBlank') }}
                <span class="required-field-star">*</span>
              </label>
              <b-input
                v-model="dataForm.blank"
                @blur="$v.dataForm.blank.$touch()"
                :placeholder="$t('strictBlank')"
                type="text"
              />
              <ValidationAlert
                v-if="$v.dataForm.blank.$dirty && !$v.dataForm.blank.required"
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
                  v-model="dataForm.dateIssue"
                  @blur="$v.dateIssueObject.$touch()"
                  type="date"
                />
                <b-input-group-append>
                  <b-form-datepicker
                    v-model="dataForm.dateIssue"
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
                v-else-if="$v.dateIssueObject.$dirty && (!$v.dateIssueObject.minValue || !$v.dateIssueObject.maxValue)"
                :text="$t('dateIssuedValid')"
              />
            </div>
          </div>
        </b-card-text>
      </b-tab>
      <b-tab
        v-if="checkAccess('serviceRecordBook', 'createExistDoc')"
        @click="checkNewRecord = false"
        :active="!checkNewRecord"
      >
        <template #title>
          <div class="text-uppercase">
            {{ $t('addExist') }}
          </div>
        </template>
        <b-card-text class="text-left d-flex wrap">
          <div class="col-6 mb-1">
            <label>
              {{ $t('number') }}
              <span class="required-field-star">*</span>
            </label>
            <b-input
              v-model="dataForm.number"
              @blur="$v.dataForm.number.$touch()"
              :placeholder="$t('number')"
              type="text"
            />
            <ValidationAlert
              v-if="($v.dataForm.number.$dirty && !$v.dataForm.number.required)"
              :text="$t('emptyField')"
            />
            <ValidationAlert
              v-else-if="($v.dataForm.number.$dirty && !$v.dataForm.number.numeric)"
              :text="$t('noNumeric')"
            />
          </div>
          <div class="col-6 mb-1">
            <label>
              {{ $t('dateIssue') }}
              <span class="required-field-star">*</span>
            </label>
            <b-input-group>
              <b-form-input
                v-model="dataForm.dateIssue"
                @blur="$v.dateIssueObject.$touch()"
                type="date"
              />
              <b-input-group-append>
                <b-form-datepicker
                  v-model="dataForm.dateIssue"
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
              v-else-if="$v.dateIssueObject.$dirty && (!$v.dateIssueObject.minValue || !$v.dateIssueObject.maxValue)"
              :text="$t('dateIssuedValid')"
            />
          </div>

          <div class="col-12 pt-0 mb-1">
            <label>
              {{ $t('affiliate') }}
              <span class="required-field-star">*</span>
            </label>
            <multiselect
              v-model="dataForm.affiliate"
              @close="$v.dataForm.affiliate.$touch()"
              :searchable="true"
              :options="mappingAffiliate"
              :placeholder="$t('affiliate')"
              :label="labelName"
              track-by="id"
            />
            <ValidationAlert
              v-if="($v.dataForm.affiliate.$dirty && !$v.dataForm.affiliate.required)"
              :text="$t('emptyField')"
             />
          </div>

          <label class="w-100">
            {{ $t('agent') }} - {{ $t('nameUK') }}
            <span class="required-field-star">*</span>
          </label>

          <div class="col-4 pt-0 mb-1">
            <b-input
              v-model="dataForm.agentLNameUK"
              @blur="$v.dataForm.agentLNameUK.$touch()"
              :placeholder="$t('lastName')"
              type="text"
            />
            <ValidationAlert
              v-if="($v.dataForm.agentLNameUK.$dirty && !$v.dataForm.agentLNameUK.required)"
              :text="$t('emptyField')"
            />
            <ValidationAlert
              v-else-if="($v.dataForm.agentLNameUK.$dirty && !$v.dataForm.agentLNameUK.maxLength)"
              :text="$t('tooLongLastName')"
            />
            <ValidationAlert
              v-else-if="($v.dataForm.agentLNameUK.$dirty && !$v.dataForm.agentLNameUK.alphaUA)"
              :text="$t('noAlphaUA')"
            />
          </div>
          <div class="col-4 pt-0 mb-1">
            <b-input
              v-model="dataForm.agentFNameUK"
              @blur="$v.dataForm.agentFNameUK.$touch()"
              :placeholder="$t('name')"
              type="text"
            >
            </b-input>
            <ValidationAlert
              v-if="($v.dataForm.agentFNameUK.$dirty && !$v.dataForm.agentFNameUK.required)"
              :text="$t('emptyField')"
            />
            <ValidationAlert
              v-else-if="($v.dataForm.agentFNameUK.$dirty && !$v.dataForm.agentFNameUK.maxLength)"
              :text="$t('tooLongCaptName')"
            />
            <ValidationAlert
              v-else-if="($v.dataForm.agentFNameUK.$dirty && !$v.dataForm.agentFNameUK.alphaUA)"
              :text="$t('noAlphaUA')"
            />
          </div>
          <div class="col-4 pt-0 mb-1">
            <b-input
              v-model="dataForm.agentMNameUK"
              @blur="$v.dataForm.agentMNameUK.$touch()"
              :placeholder="$t('middleName')"
              type="text"
            />
            <ValidationAlert
              v-if="($v.dataForm.agentMNameUK.$dirty && !$v.dataForm.agentMNameUK.maxLength)"
              :text="$t('tooLongMiddleName')"
            />
            <ValidationAlert
              v-else-if="($v.dataForm.agentMNameUK.$dirty && !$v.dataForm.agentMNameUK.alphaUA)"
              :text="$t('noAlphaUA')"
            />
          </div>

          <label class="w-100">
            {{ $t('agent') }} - {{ $t('nameEN') }}
            <span class="required-field-star">*</span>
          </label>

          <div class="col-4 pt-0 mb-1">
              <b-input
                v-model="dataForm.agentLNameEN"
                @blur="$v.dataForm.agentLNameEN.$touch()"
                :placeholder="$t('lastName')"
                type="text"
              />
              <ValidationAlert
                v-if="($v.dataForm.agentLNameEN.$dirty && !$v.dataForm.agentLNameEN.required)"
                :text="$t('emptyField')"
              />
              <ValidationAlert
                v-else-if="($v.dataForm.agentLNameEN.$dirty && !$v.dataForm.agentLNameEN.alphaEN)"
                :text="$t('noAlpha')"
              />
              <ValidationAlert
                v-else-if="($v.dataForm.agentLNameEN.$dirty && !$v.dataForm.agentLNameEN.maxLength)"
                :text="$t('tooLongLastName')"
              />
            </div>
          <div class="col-4 pt-0 mb-1">
            <b-input
              v-model="dataForm.agentFNameEN"
              @blur="$v.dataForm.agentFNameEN.$touch()"
              :placeholder="$t('name')"
              type="text"
            />
            <ValidationAlert
              v-if="($v.dataForm.agentFNameEN.$dirty && !$v.dataForm.agentFNameEN.required)"
              :text="$t('emptyField')"
            />
            <ValidationAlert
              v-else-if="($v.dataForm.agentFNameEN.$dirty && !$v.dataForm.agentFNameEN.alphaEN)"
              :text="$t('noAlpha')"
            />
            <ValidationAlert
              v-else-if="($v.dataForm.agentFNameEN.$dirty && !$v.dataForm.agentFNameEN.alphaEN)"
              :text="$t('tooLongCaptName')"
            />
          </div>
          <div class="col-4 pt-0 mb-1">
            <b-input
              v-model="dataForm.agentMNameEN"
              @blur="$v.dataForm.agentMNameEN.$touch()"
              :placeholder="$t('middleName')"
              type="text"
            />
            <ValidationAlert
              v-if="($v.dataForm.agentMNameEN.$dirty && !$v.dataForm.agentMNameEN.alphaEN)"
              :text="$t('noAlpha')"
            />
            <ValidationAlert
              v-else-if="($v.dataForm.agentMNameEN.$dirty && !$v.dataForm.agentMNameEN.maxLength)"
              :text="$t('tooLongMiddleName')"
            />
          </div>

          <div class="col-12 form-group text-left mt-2">
            <FileDropZone ref="mediaContent" />
          </div>
        </b-card-text>
      </b-tab>
    </b-tabs>
    <b-overlay
      :show="dataForm.buttonLoader"
      spinner-variant="primary"
      opacity="0.65"
      blur="2px"
      variant="white"
      class="w-100 mt-3"
      spinner-small
    >
      <b-button
        @click="checkInfo"
        class="mt-1"
        variant="success"
      >
      {{ $t('save') }}
    </b-button>
    </b-overlay>
  </b-form>
</template>

<script src="./SailorRecordBookAdd.js"/>
