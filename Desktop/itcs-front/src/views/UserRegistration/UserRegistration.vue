<template>
  <div>
    <div class="vx-card disable-rounded-right p-2 mb-1">
      <div class="card-header">
        <div class="card-title">
          <h4 class="text-center">
            {{ $t('addUbikey') }}
          </h4>
        </div>
      </div>
      <div class="card-content pt-3">
        <AddUbikeyToLogin :fingerRegistration="registerFingerFirst"/>
      </div>
    </div>

    <div class="vx-card p-2 mt-3">
      <div class="card-header">
        <div class="card-title">
          <h4 class="text-center">
            {{ $t('addUser') }}
          </h4>
        </div>
      </div>
      <div class="card-content pt-3">
        <b-form @submit.prevent="checkUserInfo">
          <div class="pageList">
            <div class="w-full permissionChoice">
              <div class="w-full permissionChoiceContent">
                <div class="flex items-end align-items-center">
                  <span>
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="26px"
                      height="26px"
                      viewBox="0 0 30 30"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    >
                      <rect
                        x="3"
                        y="11"
                        width="19"
                        height="15"
                        rx="5"
                        ry="2"
                      />
                      <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                    </svg>
                  </span>
                  <span class="font-normal text-lg leading-none">
                    {{ $t('permissions') }}
                  </span>
                </div>
                <div class="vs-component vs-divider">
                  <span
                    class="vs-divider-border after vs-divider-border-default"
                    style="width: 100%; border-top: 1px solid rgba(0, 0, 0, 0.1);"
                  />
                  <span
                    class="vs-divider-border before vs-divider-border-default"
                    style="width: 100%; border-top: 1px solid rgba(0, 0, 0, 0.1);"
                  />
                </div>
                <b-form-group>
                  <b-form-radio-group
                    v-model="dataForm.permission"
                    :options="permissionsList"
                    value-field="text"
                    text-field="text"
                    stacked
                  />
                  <ValidationAlert
                    v-if="$v.dataForm.permission.$dirty && !$v.dataForm.permission.required"
                    :text="$t('emptyField')"
                  />
                </b-form-group>
              </div>
            </div>
            <div
              v-if="dataForm.permission !== 'Мед. працівник'"
              class="w-33"
            >
              <b>{{ $t('lastName') }} *</b>
              <b-form-input
                v-model="dataForm.lastName"
                @blur="$v.dataForm.lastName.$touch()"
                :placeholder="$t('lastName')"
                type="text"
              />
              <ValidationAlert
                v-if="$v.dataForm.lastName.$dirty && !$v.dataForm.lastName.required"
                :text="$t('emptyField')"
              />
              <ValidationAlert
                v-else-if="$v.dataForm.lastName.$dirty && !$v.dataForm.lastName.maxLength"
                :text="$t('tooLongLastName')"
              />
              <ValidationAlert
                v-else-if="$v.dataForm.lastName.$dirty && !$v.dataForm.lastName.alphaLang"
                :text="$t('invalidDataFormat')"
              />
            </div>
            <div
              v-if="dataForm.permission !== 'Мед. працівник'"
              class="w-33"
            >
              <b>{{ $t('name') }} *</b>
              <b-form-input
                v-model="dataForm.firstName"
                @blur="$v.dataForm.firstName.$touch()"
                :placeholder="$t('name')"
                type="text"
              />
              <ValidationAlert
                v-if="$v.dataForm.firstName.$dirty && !$v.dataForm.firstName.required"
                :text="$t('emptyField')"
              />
              <ValidationAlert
                v-else-if="$v.dataForm.firstName.$dirty && !$v.dataForm.firstName.maxLength"
                :text="$t('tooLongCaptName')"
              />
              <ValidationAlert
                v-else-if="$v.dataForm.firstName.$dirty && !$v.dataForm.firstName.alphaLang"
                :text="$t('invalidDataFormat')"
              />
            </div>
            <div
              v-if="dataForm.permission !== 'Мед. працівник'"
              class="w-33"
            >
              <b>{{ $t('middleName') }} *</b>
              <b-form-input
                v-model="dataForm.middleName"
                @blur="$v.dataForm.middleName.$touch()"
                :placeholder="$t('middleName')"
                type="text"
              />
              <ValidationAlert
                v-if="$v.dataForm.middleName.$dirty && !$v.dataForm.middleName.required"
                :text="$t('emptyField')"
              />
              <ValidationAlert
                v-else-if="$v.dataForm.middleName.$dirty && !$v.dataForm.middleName.maxLength"
                :text="$t('tooLongMiddleName')"
              />
              <ValidationAlert
                v-else-if="$v.dataForm.middleName.$dirty && !$v.dataForm.middleName.alphaLang"
                :text="$t('invalidDataFormat')"
              />
            </div>

            <div v-if="dataForm.permission === 'Мед. працівник'" class="w-100">
              <b>{{ $t('medicalInstitution') }} *</b>
              <multiselect
                v-model="dataForm.medical"
                @close="$v.dataForm.medical.$touch()"
                :placeholder="$t('medicalInstitution')"
                :searchable="true"
                :options="mappingMedicalInstitutions"
                label="value"
                track-by="id"
              />
              <ValidationAlert
                v-if="$v.dataForm.medical.$dirty && !$v.dataForm.medical.required"
                :text="$t('emptyField')"
              />
            </div>
            <div
              v-if="dataForm.permission === 'Мед. працівник'"
              class="w-100"
            >
              <b>{{ $t('doctor') }} *</b>
              <multiselect
                v-model="dataForm.doctor"
                @close="$v.dataForm.doctor.$touch()"
                :placeholder="$t('doctor')"
                :searchable="true"
                :options="mappingDoctors(dataForm.medical)"
                label="FIO"
                track-by="id"
              />
              <ValidationAlert
                v-if="$v.dataForm.doctor.$dirty && !$v.dataForm.doctor.required"
                :text="$t('emptyField')"
              />
            </div>

            <div class="w-50">
              <b>{{ $t('login') }} *</b>
              <b-form-input
                v-model="dataForm.login"
                @blur="$v.dataForm.login.$touch()"
                :placeholder="$t('login')"
                type="text"
              />
              <ValidationAlert
                v-if="$v.dataForm.login.$dirty && !$v.dataForm.login.required"
                :text="$t('emptyField')"
              />
              <ValidationAlert
                v-else-if="$v.dataForm.login.$dirty && !$v.dataForm.login.validLogin"
                :text="$t('invalidDataFormat')"
              />
            </div>
            <div class="w-50">
              <b>{{ $t('pass') }} *</b>
              <b-form-input
                v-model="dataForm.pass"
                @blur="$v.dataForm.pass.$touch()"
                :placeholder="$t('pass')"
                type="password"
              />
              <ValidationAlert
                v-if="$v.dataForm.pass.$dirty && !$v.dataForm.pass.required"
                :text="$t('emptyField')"
              />
            </div>
            <div class="w-25">
              <b>{{ $t('country') }} *</b>
              <multiselect
                v-model="dataForm.country"
                @close="$v.dataForm.country.$touch()"
                :searchable="true"
                :options="mappingCountry"
                :placeholder="$t('country')"
                :label="labelValue"
                track-by="id"
              />
              <ValidationAlert
                v-if="$v.dataForm.country.$dirty && !$v.dataForm.country.required"
                :text="$t('emptyField')"
              />
            </div>
            <div class="w-25">
              <b>{{ $t('region') }} *</b>
              <multiselect
                v-model="dataForm.region"
                @input="mappingCities(dataForm.region)"
                @close="$v.dataForm.region.$touch()"
                :placeholder="$t('region')"
                :searchable="true"
                :options="mappingRegion(dataForm.country)"
                :label="labelValue"
                track-by="id"
              >
                <span slot="noOptions">
                  {{ $t('selectCountry') }}
                </span>
              </multiselect>
              <ValidationAlert
                v-if="$v.dataForm.region.$dirty && !$v.dataForm.region.required"
                :text="$t('emptyField')"
              />
            </div>
            <div :class="dataForm.permission === 'Мед. працівник' ? 'w-50' : 'w-25'">
              <b>{{ $t('city') }} *</b>
              <multiselect
                v-model="dataForm.city"
                @close="$v.dataForm.city.$touch()"
                :placeholder="$t('city')"
                :searchable="true"
                :options="cityList"
                :label="labelValue"
                track-by="id"
              >
                <span slot="noOptions">
                  {{ $t('selectRegion') }}
                </span>
              </multiselect>
              <ValidationAlert
                v-if="$v.dataForm.city.$dirty && !$v.dataForm.city.required"
                :text="$t('emptyField')"
              />
            </div>
            <div v-if="dataForm.permission !== 'Мед. працівник'" class="w-25">
              <b>
                {{ $t('affiliate') }} *
              </b>
              <multiselect
                v-model="dataForm.affiliate"
                @close="$v.dataForm.affiliate.$touch()"
                :placeholder="$t('affiliate')"
                :searchable="true"
                :options="mappingAffiliate"
                :label="labelName"
                track-by="id"
              />
              <ValidationAlert
                v-if="$v.dataForm.affiliate.$dirty && !$v.dataForm.affiliate.required"
                :text="$t('emptyField')"
              />
            </div>

            <div v-if="dataForm.permission === 'Представник НТЗ' || dataForm.permission === 'Секретар КПК'" class="w-100">
              <b>
                {{ $t('nameInstitution') }} *
              </b>
              <multiselect
                v-model="dataForm.institution"
                @close="$v.dataForm.institution.$touch()"
                :placeholder="$t('nameInstitution')"
                :searchable="true"
                :options="dataForm.permission === 'Представник НТЗ' ? mappingTrainingPlace : mappingInstitutionList"
                :label="labelName"
                track-by="id"
              />
              <ValidationAlert
                v-if="$v.dataForm.institution.$dirty && !$v.dataForm.institution.required"
                :text="$t('emptyField')"
              />
            </div>

            <div
              v-if="dataForm.permission === 'Довірена особа' || dataForm.permission === 'Керівник групи' ||
               dataForm.permission === 'Секретар КПК'"
              class="w-50"
            >
              <b>{{ $t('phoneNumber') }} *</b>
              <phone-mask-input
                v-model="dataForm.phoneNumber"
                @onBlur="$v.dataForm.phoneNumber.$touch()"
                :placeholder="$t('phoneNumber')"
                class="w-full mainInfoPhone"
              />
              <ValidationAlert
                v-if="$v.dataForm.phoneNumber.$dirty && !$v.dataForm.phoneNumber.required"
                :text="$t('emptyField')"
              />
              <div
                v-if="dataForm.permission === 'Довірена особа' || dataForm.permission === 'Керівник групи'"
                class="w-100 d-flex"
              >
                <b-form-checkbox
                  v-model="dataForm.telegramFlag"
                  :value="true"
                  :unchecked-value="false"
                  name="telegram"
                  class="w-25 d-flex justify-content-start align-items-center"
                >
                  Telegram
                </b-form-checkbox>
                <phone-mask-input
                  v-if="dataForm.telegramFlag"
                  v-model="dataForm.telegramNumber"
                  @onBlur="$v.dataForm.telegramNumber.$touch()"
                  :placeholder="$t('phoneNumber')"
                  class="w-75 mainInfoPhone"
                />
                <ValidationAlert
                  v-if="$v.dataForm.telegramNumber.$dirty && !$v.dataForm.telegramNumber.required"
                  :text="$t('emptyField')"
                />
              </div>
              <div
                v-if="dataForm.permission === 'Довірена особа' || dataForm.permission === 'Керівник групи'"
                class="w-100 d-flex"
              >
                <b-form-checkbox
                  v-model="dataForm.viberFlag"
                  :value="true"
                  :unchecked-value="false"
                  name="telegram"
                  class="w-25 d-flex justify-content-start align-items-center"
                >
                  Viber
                </b-form-checkbox>
                <phone-mask-input
                  v-if="dataForm.viberFlag"
                  v-model="dataForm.viberNumber"
                  @onBlur="$v.dataForm.viberNumber.$touch()"
                  :placeholder="$t('phoneNumber')"
                  class="w-75 mainInfoPhone"
                />
                <ValidationAlert
                  v-if="$v.dataForm.viberNumber.$dirty && !$v.dataForm.viberNumber.required"
                  :text="$t('emptyField')"
                />
              </div>
            </div>

            <div v-if="dataForm.permission === 'Секретар КПК'" class="w-50">
              <b>{{ $t('email') }} *</b>
              <b-form-input
                v-model="dataForm.email"
                @blur="$v.dataForm.email.$touch()"
                :placeholder="$t('email')"
                type="text"
              />
              <ValidationAlert
                v-if="$v.dataForm.email.$dirty && !$v.dataForm.email.required"
                :text="$t('emptyField')"
              />
              <ValidationAlert
                v-else-if="$v.dataForm.email.$dirty && !$v.dataForm.email.email"
                :text="$t('invalidEmail')"
              />
            </div>

            <div
              v-if="dataForm.permission === 'Довірена особа' ||
                dataForm.permission === 'Керівник групи' ||
                dataForm.permission === 'Секретар СЦ'"
              class="w-50"
            >
              <b>
                {{ $t('agentGroups') }} *
              </b>
              <multiselect
                v-model="dataForm.agentGroup"
                @close="$v.dataForm.agentGroup.$touch()"
                :multiple="dataForm.permission === 'Секретар СЦ'"
                :placeholder="$t('agentGroups')"
                :searchable="true"
                :options="mappingAgentGroups"
                :label="labelName"
                track-by="id"
              />
              <ValidationAlert
                v-if="$v.dataForm.agentGroup.$dirty && !$v.dataForm.agentGroup.required"
                :text="$t('emptyField')"
              />
            </div>
            <div v-if="dataForm.permission === 'Довірена особа' || dataForm.permission === 'Керівник групи'">
              <FileDropZone ref="mediaContent" class="w-100 text-left" />
              <ValidationAlert
                v-if="$v.mediaFilesArray.$dirty && !$v.mediaFilesArray.required"
                :text="$t('emptyField')"
              />
            </div>

            <div class="w-full">
              <b-form-checkbox
                v-model="registrationVariant"
                :value="false"
                name="authorizationVariant"
                class="pb-1"
              >
                {{ $t('registerWithUbikey') }}
              </b-form-checkbox>
            </div>
            <div class="w-full">
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
                  type="submit"
                  variant="success"
                  class="mt-1"
                >
                  {{ $t('registration') }}
                </b-button>
              </b-overlay>
            </div>
          </div>
        </b-form>
        <h5
          v-if="dataForm.addFingetTitle"
          class="text-center card-title"
        >
          {{ $t('fingerTite') }}
        </h5>
      </div>
    </div>
  </div>
</template>

<script src="./UserRegistration.js"></script>
