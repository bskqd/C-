<template>
  <b-form @submit.prevent="checkDataForAddNewDocument">
    <b-tabs fill pills>
      <b-tab
        v-if="checkAccess('sailorPassport', 'addExistPassport')"
        @click="newSailorPassport = false"
        active
      >
        <template slot="title">
          <div class="text-uppercase">
            {{ $t('addExistSailorPassport') }}
          </div>
        </template>
        <b-card-text>
          <div class="text-left">
            <div class="flex-row-sb form-group">
              <div class="col-6">
                <label>
                  {{ $t('country') }}
                  <span class="required-field-star">*</span>
                </label>
                <multiselect
                  v-model="dataForm.country"
                  @close="$v.dataForm.country.$touch()"
                  :options="mappingCountry"
                  :searchable="true"
                  :placeholder="$t('country')"
                  :label="labelValue"
                  track-by="id"
                />
                <ValidationAlert
                  v-if="$v.dataForm.country.$dirty && !$v.dataForm.country.required"
                  :text="$t('emptyField')"
                />
              </div>
              <div class="col-6">
                <label>
                  {{ $t('port') }}
                  <span class="required-field-star">*</span>
                </label>
                <b-input
                  v-if="dataForm.country && dataForm.country.id !== 2"
                  v-model="dataForm.portOther"
                  @blur="$v.dataForm.portOther.$touch()"
                  :placeholder="$t('port')"
                  type="text"
                />
                <ValidationAlert
                  v-if="$v.dataForm.portOther.$dirty && !$v.dataForm.portOther.required"
                  :text="$t('emptyField')"
                />
                <multiselect
                  v-else-if="!dataForm.country || (dataForm.country && dataForm.country.id === 2)"
                  v-model="dataForm.port"
                  @close="$v.dataForm.port.$touch()"
                  :options="mappingPort"
                  :searchable="true"
                  :placeholder="$t('port')"
                  :label="labelName"
                  track-by="id"
                />
                <ValidationAlert
                  v-if="$v.dataForm.port.$dirty && !$v.dataForm.port.required"
                  :text="$t('emptyField')"
                />
              </div>
            </div>

            <div class="flex-row-sb form-group mt-2">
              <div class="col-6">
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
                  v-if="$v.dataForm.number.$dirty && !$v.dataForm.number.required"
                  :text="$t('emptyField')"
                />
                <ValidationAlert
                  v-else-if="$v.dataForm.number.$dirty && !$v.dataForm.number.maxLength"
                  :text="$t('tooLongSailorPassNum')"
                />
              </div>
              <div class="col-6">
                <label v-if="dataForm.country && dataForm.country.id === 2">
                  {{ $t('issuedBy') }}
                  <span class="required-field-star">*</span>
                </label>
                <label v-else>
                  {{ $t('captain') }}
                  <span class="required-field-star">*</span>
                </label>
                <b-input
                  v-model="dataForm.captain"
                  @blur="$v.dataForm.captain.$touch()"
                  :placeholder="$t('captain')"
                  type="text"
                />
                <ValidationAlert
                  v-if="$v.dataForm.captain.$dirty && !$v.dataForm.captain.required"
                  :text="$t('emptyField')"
                />
                <ValidationAlert
                  v-else-if="$v.dataForm.captain.$dirty && !$v.dataForm.captain.maxLength"
                  :text="$t('tooLongCaptName')"
                />
              </div>
            </div>

            <div class="flex-row-sb form-group mt-2">
              <div class="col-4">
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
                      @input="$v.dateIssueObject.$touch()"
                      :locale="lang"
                      :max="sevenDaysAgoDate"
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
                  v-if="$v.dateIssueObject.$dirty && (!$v.dateIssueObject.maxValue || !$v.dateIssueObject.minValue)"
                  :text="$t('sevenDaysDate')"
                />
              </div>
              <div class="col-4">
                <label>
                  {{ $t('dateTermination') }}
                  <span class="required-field-star">*</span>
                </label>
                <b-input-group>
                  <b-form-input
                    v-model="dataForm.dateTermination"
                    @blur="$v.dateTerminationObject.$touch()"
                    type="date"
                  />
                  <b-input-group-append>
                    <b-form-datepicker
                      v-model="dataForm.dateTermination"
                      @input="$v.dateTerminationObject.$touch()"
                      :locale="lang"
                      :min="dataForm.dateIssue"
                      max="2200-12-31"
                      start-weekday="1"
                      button-only
                      right
                    />
                  </b-input-group-append>
                </b-input-group>
                <ValidationAlert
                  v-if="($v.dateTerminationObject.$dirty && !$v.dateTerminationObject.required)"
                  :text="$t('emptyField')"
                />
                <ValidationAlert
                  v-if="$v.dateTerminationObject.$dirty &&
              (!$v.dateTerminationObject.maxValue || !$v.dateTerminationObject.minValue)"
                  :text="$t('dateTerminateValid')"
                />
              </div>
              <div class="col-4">
                <label>
                  {{ $t('dateRenewal') }}
                </label>
                <b-input-group>
                  <b-form-input
                    v-model="dataForm.dateRenewal"
                    @blur="$v.dateRenewalObject.$touch()"
                    type="date"
                  />
                  <b-input-group-append>
                    <b-form-datepicker
                      v-model="dataForm.dateRenewal"
                      @input="$v.dateRenewalObject.$touch()"
                      :locale="lang"
                      :min="dataForm.dateTermination"
                      max="2200-12-31"
                      start-weekday="1"
                      button-only
                      right
                    />
                  </b-input-group-append>
                </b-input-group>
                <ValidationAlert
                  v-if="$v.dateRenewalObject.$dirty && (!$v.dateRenewalObject.maxValue || !$v.dateRenewalObject.minValue)"
                  :text="$t('dateRenewalValid')"
                />
              </div>
            </div>

            <div class="col-12 form-group text-left mt-2">
              <label>
                {{ $t('strictBlank') }}
              </label>
              <b-input
                v-model="dataForm.strictBlank"
                @blur="$v.dataForm.strictBlank.$touch()"
                :placeholder="$t('strictBlank')"
                type="number"
              />
              <ValidationAlert
                v-if="$v.dataForm.strictBlank.$dirty && !$v.dataForm.strictBlank.numeric"
                :text="$t('noNumeric')"
              />
            </div>

            <div class="col-12 form-group text-left mt-2">
              <FileDropZone ref="mediaContent" />
            </div>
          </div>
        </b-card-text>
      </b-tab>

      <b-tab
        v-if="checkAccess('sailorPassport', 'addNewPassport')"
        @click="newSailorPassport = true"
      >
        <template slot="title">
          <div class="text-uppercase">
            {{ $t('addNewSailorPassport') }}
          </div>
        </template>
        <b-card-text>
          <div class="text-left d-flex flex-wrap">
            <div class="w-100">
              <label>
                {{ $t('number') }}
                <span class="required-field-star">*</span>
              </label>
              <b-form-input
                v-model="dataForm.number"
                @blur="$v.dataForm.number.$touch()"
                :placeholder="$t('number')"
                type="text"
              />
              <ValidationAlert
                v-if="$v.dataForm.number.$dirty && !$v.dataForm.number.required"
                :text="$t('emptyField')"
              />
              <ValidationAlert
                v-else-if="$v.dataForm.number.$dirty && !$v.dataForm.number.maxLength"
                :text="$t('tooLongSailorPassNum')"
              />
            </div>
            <div class="w-100 mt-3">
              <label>
                {{ $t('approvedStatements') }}
                <span class="required-field-star">*</span>
              </label>
              <multiselect
                v-model="dataForm.approvedStatement"
                :options="existStatements"
                :searchable="true"
                :placeholder="$t('approvedStatements')"
                label="fullName"
                track-by="id"
              >
                <span slot="noOptions">
                  {{ $t('notFind') }}
                </span>
              </multiselect>
              <ValidationAlert
                v-if="$v.dataForm.approvedStatement.$dirty && !$v.dataForm.approvedStatement.required"
                :text="$t('emptyField')"
              />
            </div>
            <div
              v-if="dataForm.approvedStatement && dataForm.approvedStatement.is_continue"
              class="w-100 mt-3"
            >
              <label>
                {{ $t('continuingStatement') }}
                <span class="required-field-star">*</span>
              </label>
              <multiselect
                v-model="dataForm.continuingPassport"
                :options="allowToContinuePassport"
                :searchable="true"
                :placeholder="$t('continuingStatement')"
                label="fullName"
                track-by="id"
              >
                <span slot="noOptions">
                  {{ $t('notFind') }}
                </span>
              </multiselect>
              <ValidationAlert
                v-if="$v.dataForm.continuingPassport.$dirty && !$v.dataForm.continuingPassport.required"
                :text="$t('emptyField')"
              />
            </div>
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
      class="w-100"
      spinner-small
    >
      <b-button
        class="mt-1"
        type="submit"
        variant="success"
      >
        {{ $t('save') }}
      </b-button>
    </b-overlay>
  </b-form>
</template>

<script src="./SailorPassportAdd.js"/>
