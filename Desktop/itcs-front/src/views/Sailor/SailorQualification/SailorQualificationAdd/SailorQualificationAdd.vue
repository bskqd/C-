<template>
  <b-form @submit.prevent="checkNewDoc">
    <b-tabs fill pills>
      <b-tab
        v-if="checkAccess('qualification', 'createNewQualification')"
        @click="checkNewQualDoc(true)"
        active
      >
        <template slot="title">
          <div class="text-uppercase">
            {{ $t('addNewQualificationDoc') }}
          </div>
        </template>
        <b-card-text>
          <div class="text-left">
            <div class="flex-row-sb form-group">
              <div class="col-12">
                <label>
                  {{ $t('approvedStatements') }}
                  <span class="required-field-star">*</span>
                </label>
                <multiselect
                  v-model="dataForm.statements"
                  @close="$v.dataForm.statements.$touch()"
                  :options="existStatements"
                  :searchable="true"
                  :placeholder="$t('approvedStatements')"
                  :label="labelName"
                  track-by="id"
                >
                  <span slot="noOptions">
                    {{ $t('notFind') }}
                  </span>
                </multiselect>
                <ValidationAlert
                  v-if="$v.dataForm.statements.$dirty && !$v.dataForm.statements.required"
                  :text="$t('emptyField')"
                />
              </div>
            </div>
<!--            <div-->
<!--              v-if="viewDiplomaInNewDoc"-->
<!--              class="flex-row-sb form-group mt-2"-->
<!--            >-->
            <div
              v-if="dataForm.statements && dataForm.statements.type_document.id === 16"
              class="flex-row-sb form-group mt-2"
            >
              <div class="col-12">
                <label>
                  {{ $t('diploma') }}
                  <span class="required-field-star">*</span>
                </label>
<!--                <multiselect-->
<!--                  v-model="dataForm.diplomaInNewDoc"-->
<!--                  @close="$v.dataForm.diplomaInNewDoc.$touch()"-->
<!--                  :options="mappingDiplomasByRank(dataForm.successApplication)" :searchable="true"-->
<!--                  :placeholder="$t('diploma')"-->
<!--                  label="name_ukr"-->
<!--                  track-by="id"-->
<!--                >-->
<!--                  <span slot="noOptions">-->
<!--                    {{ $t('selectApplication') }}-->
<!--                  </span>-->
<!--                </multiselect>-->
<!--                <ValidationAlert-->
<!--                  v-if="$v.dataForm.diplomaInNewDoc.$dirty && !$v.dataForm.diplomaInNewDoc.required"-->
<!--                  :text="$t('emptyField')"-->
<!--                />-->
                <multiselect
                  v-model="dataForm.diploma"
                  @close="$v.dataForm.diploma.$touch()"
                  :options="mappingDiplomasByRank(dataForm.statements)"
                  :searchable="true"
                  :placeholder="$t('diploma')"
                  label="name_ukr"
                  track-by="id"
                >
                  <span slot="noOptions">
                    {{ $t('selectStatement') }}
                  </span>
                </multiselect>
                <ValidationAlert
                  v-if="$v.dataForm.diploma.$dirty && !$v.dataForm.diploma.required"
                  :text="$t('emptyField')"
                />
              </div>
            </div>
            <div class="flex-row-sb form-group mt-2">
              <div class="col-12">
                <label>
                  {{ $t('strictBlank') }}
                  <span class="required-field-star">*</span>
                </label>
                <b-input
                  v-model="dataForm.strictBlank"
                  @blur="$v.dataForm.strictBlank.$touch()"
                  :placeholder="$t('strictBlank')"
                  type="text"
                />
                <ValidationAlert
                  v-if="$v.dataForm.strictBlank.$dirty && !$v.dataForm.strictBlank.required"
                  :text="$t('emptyField')"
                />
              </div>
            </div>
          </div>
        </b-card-text>
      </b-tab>
      <b-tab @click="checkNewQualDoc(false)">
        <template slot="title">
          <div class="text-uppercase">
            {{ $t('addExistQualificationDoc') }}
          </div>
        </template>
        <b-card-text>
          <div class="text-left">
            <div class="flex-row-sb form-group mt-2">
              <div class="col-12">
                <label>
                  {{ $t('typeDoc') }}
                  <span class="required-field-star">*</span>
                </label>
                <multiselect
                  v-model="dataForm.type"
                  @input="checkTypeDocument"
                  @close="$v.dataForm.type.$touch()"
                  :options="typeDocQual"
                  :searchable="true"
                  :placeholder="$t('typeDoc')"
                  :label="labelName"
                  track-by="id"
                />
                <ValidationAlert
                  v-if="$v.dataForm.type.$dirty && !$v.dataForm.type.required"
                  :text="$t('emptyField')"
                />
              </div>
            </div>
            <div
              v-if="viewNumber"
              class="flex-row-sb form-group"
            >
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
                  :text="$t('tooLongNumDoc')"
                />
              </div>
              <div class="col-6">
                <label>
                  {{ $t('country') }}
                  <span class="required-field-star">*</span>
                </label>
                <multiselect
                  v-model="dataForm.country"
                  @close="$v.dataForm.country.$touch()"
                  @input="dataForm.port = null"
                  :options="countryOptions"
                  :searchable="true"
                  :placeholder="$t('country')"
                  :label="langCountry"
                  track-by="id"
                />
                <ValidationAlert
                  v-if="$v.dataForm.country.$dirty && !$v.dataForm.country.required"
                  :text="$t('emptyField')"
                />
              </div>
            </div>

            <div class="flex-row-sb form-group mt-2">
              <div class="col-12">
                <label>
                  {{ $t('port') }}
                  <span class="required-field-star">*</span>
                </label>
                <multiselect
                  v-if="dataForm.country.id === 2"
                  v-model="dataForm.port"
                  @close="$v.dataForm.port.$touch()"
                  :options="ports"
                  :searchable="true"
                  :placeholder="$t('port')"
                  :label="labelName"
                  track-by="id"
                />
                <b-input
                  v-else
                  v-model="dataForm.port"
                  @blur="$v.dataForm.port.$touch()"
                  :placeholder="$t('port')"
                  type="text"
                >
                </b-input>

                <ValidationAlert
                  v-if="$v.dataForm.port.$dirty && !$v.dataForm.port.required"
                  :text="$t('emptyField')"
                />
              </div>
            </div>
            <div
              v-if="viewDiploma"
              class="flex-row-sb form-group"
            >
              <div class="col-12">
                <label>
                  {{ $t('diploma') }}
                  <span class="required-field-star">*</span>
                </label>
                <multiselect
                  v-model="dataForm.diploma"
                  @close="$v.dataForm.diploma.$touch()"
                  @input="mappingFunctionByPosition(dataForm.diploma.list_positions)"
                  :options="diplomas"
                  :searchable="true"
                  :placeholder="$t('diploma')"
                  :label="labelName"
                  track-by="id"
                />
                <ValidationAlert
                  v-if="$v.dataForm.diploma.$dirty && !$v.dataForm.diploma.required"
                  :text="$t('emptyField')"
                />
              </div>
            </div>
            <div
              v-if="!viewDiploma"
              class="flex-row-sb form-group mt-2"
            >
              <div class="col-12">
                <label>
                  {{ $t('rank') }}
                  <span class="required-field-star">*</span>
                </label>
                <multiselect
                  v-model="dataForm.rank"
                  @close="$v.dataForm.rank.$touch()"
                  @input="clearPosition(dataForm.rank, dataForm.position)"
                  :options="ranks"
                  :searchable="true"
                  :placeholder="$t('rank')"
                  :label="labelName"
                  track-by="id"
                />
                <ValidationAlert
                  v-if="$v.dataForm.rank.$dirty && !$v.dataForm.rank.required"
                  :text="$t('emptyField')"
                />
              </div>
            </div>
            <div
              v-if="!viewDiploma"
              class="flex-row-sb form-group mt-2"
            >
              <div class="col-12">
                <label>
                  {{ $t('position') }}
                  <span class="required-field-star">*</span>
                </label>
                <multiselect
                  v-model="dataForm.position"
                  @close="$v.dataForm.position.$touch()"
                  :searchable="true"
                  :options="mappingPositions(dataForm.rank)"
                  :placeholder="$t('position')"
                  :label="labelName"
                  track-by="id"
                  multiple
                >
                  <span slot="noOptions">
                    {{ $t('selectRank') }}
                  </span>
                </multiselect>
                <ValidationAlert
                  v-if="$v.dataForm.position.$dirty && !$v.dataForm.position.required"
                  :text="$t('emptyField')"
                />
              </div>
            </div>
            <div
              v-if="viewLimitation && dataForm.diploma"
              class="flex-row-sb form-group"
            >
              <div class="col-12">
                <label>
                  {{ $t('limitation') }}:
                </label>
                <div
                  v-for="(func, index) of dataForm.functionPosition"
                  :key="func.id"
                  class="mt-1"
                >
                  <span>
                    {{ func.function[labelName] }}
                  </span>
                  <multiselect
                    v-if="func.function.name_ukr !== 'немає'"
                    v-model="dataForm.limitations[index]"
                    @input="updateLimitation(index, func.id)"
                    :options="positionsLimitations"
                    :searchable="true"
                    :placeholder="$t('limitation')"
                    :label="labelName"
                    track-by="id"
                    multiple
                  />
                </div>
              </div>
            </div>
            <div class="flex-row-sb form-group mt-2 d-flex">
              <div class="col-6">
                <label>
                  {{ $t('dateIssue') }}
                  <span class="required-field-star">*</span>
                </label>
                <b-input-group>
                  <b-form-input
                    v-model="dataForm.dateStart"
                    @blur="$v.dateStartObject.$touch()"
                    type="date"
                  />
                  <b-input-group-append>
                    <b-form-datepicker
                      v-model="dataForm.dateStart"
                      @input="$v.dateStartObject.$touch()"
                      :locale="lang"
                      start-weekday="1"
                      :max="new Date()"
                      min="1900-01-01"
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
                  v-else-if="$v.dateStartObject.$dirty &&
                    (!$v.dateStartObject.maxValue || !$v.dateStartObject.minValue)"
                  :text="$t('dateIssuedValid')"
                />
              </div>
              <div
                v-if="viewDateTerm"
                class="col-6"
              >
                <label>
                  {{ $t('dateTermination') }}
                  <span class="required-field-star">*</span>
                </label>
                <b-input-group>
                  <b-form-input
                    v-model="dataForm.dateEnd"
                    @blur="$v.dateEndObject.$touch()"
                    type="date"
                  />
                  <b-input-group-append>
                    <b-form-datepicker
                      v-model="dataForm.dateEnd"
                      @input="$v.dateEndObject.$touch()"
                      :locale="lang"
                      :min="dataForm.dateStart"
                      max="2200-12-31"
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
                  v-else-if="$v.dateEndObject.$dirty &&
                    (!$v.dateEndObject.maxValue || !$v.dateEndObject.minValue)"
                  :text="$t('dateTerminateValid')"
                />
              </div>
            </div>

            <div class="flex-row-sb form-group mt-2">
              <div class="col-12">
                <label>
                  {{ $t('strictBlank') }}
                  <span class="required-field-star">*</span>
                </label>
                <b-input
                  v-model="dataForm.strictBlank"
                  @blur="$v.dataForm.strictBlank.$touch()"
                  :placeholder="$t('strictBlank')"
                  type="text"
                />
                <ValidationAlert
                  v-if="$v.dataForm.strictBlank.$dirty && !$v.dataForm.strictBlank.required"
                  :text="$t('emptyField')"
                />
              </div>
            </div>

            <div>
              <FileDropZone ref="mediaContent" />
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
      class="w-100 mt-1"
      spinner-small
    >
      <b-button
        variant="success"
        type="submit"
      >
        {{ $t('save') }}
      </b-button>
    </b-overlay>
  </b-form>
</template>

<script src="./SailorQualificationAdd.js"/>
