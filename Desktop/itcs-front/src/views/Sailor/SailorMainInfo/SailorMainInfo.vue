<template>
  <b-form @submit.prevent="validateForm()">
    <div class="mb-6 p-2">
        <div class="vx-row d-flex aic">
          <div class="seafareMainInfoAvatar">
            <div>
              <img
                v-if="sailorPhoto && sailorPhoto[0]"
                :src="sailorPhoto[0].url"
                class="avatar"
                width="125px"
                alt="sailorPhoto"
              />
            </div>
          </div>
          <div class="seafarerInfo vx-col flex-1">

          <div class="vx-row">
            <div class="col-12 form-group text-left seafarerInfo-about">
              <div class="d-flex justify-content-end align-self-start p-0 m-0 seafarerEditBtn">
                <b-button
                  v-if="checkAccess('main-editInfo') && !edit && !mini"
                  @click="startEdit()"
                  variant="outline"
                >
                  <unicon
                    name="pen"
                    fill="royalblue"
                  />
                </b-button>
                <b-button
                  v-if="edit"
                  @click="cancelEdit()"
                  variant="outline"
                >
                  <unicon
                    name="multiply"
                    fill="royalblue"
                  />
                </b-button>
                <b-button
                  v-if="edit"
                  type="submit"
                  variant="outline"
                >
                  <unicon
                    name="check"
                    fill="limegreen"
                    width="30"
                    height="30"
                  />
                </b-button>
                <b-button
                  v-if="!edit && mini"
                  @click="showAllInfo()"
                  variant="outline"
                >
                  <unicon
                    name="angle-down"
                    width="40px"
                    height="40px"
                    fill="royalblue"
                  />
                </b-button>
                <b-button
                  v-if="!edit && !mini"
                  @click="closeAllInfo()"
                  variant="outline"
                >
                  <unicon
                    name="multiply"
                    fill="royalblue"
                  />
                </b-button>
              </div>

              <div
                v-if="edit"
                class="vx-row seafarerMainInfoTitle"
              >
                  {{ $t('editSailorMainInfo') }}
              </div>
              <div
                v-if="!edit"
                class="justify-content-lg-start pl-1 seafarerInfo-name vx-row"
              >
                <div>
                  <v-icon
                    v-if="sailorInfo.exists_account"
                    color="green"
                    x-small>
                    mdi-checkbox-blank-circle
                  </v-icon>

                  {{ sailorInfo.last_name_ukr }} {{ sailorInfo.first_name_ukr }} {{ sailorInfo.middle_name_ukr }}
                </div>
                <div v-if="checkAccess('main-ratingAll')" class="rating w-25">
                  <Rating :readonly="checkAccess('main-ratingW')" :viewEditOnly="false"/>
                </div>
              </div>

              <div
                v-if="edit"
                class="form-group mt-1 mb-0"
              >
                <div class="col-12 mt-1">
                  <label class="text-bold-300">
                    {{ $t('nameUK') }}
                  </label>
                </div>
              </div>
              <div
                v-if="edit"
                class="vx-row"
              >
                <div class="col-4 pt-0">
                  <b-input
                    v-if="edit"
                    v-model="sailorInfo.last_name_ukr"
                    @blur="$v.sailorInfo.last_name_ukr.$touch()"
                    :placeholder="$t('lastName')"
                    type="text"
                    class="name form-control"
                  >
                  </b-input>
                  <ValidationAlert
                    v-if="($v.sailorInfo.last_name_ukr.$dirty && !$v.sailorInfo.last_name_ukr.required)"
                    :text="$t('emptyField')"
                  />
                  <ValidationAlert
                    v-else-if="($v.sailorInfo.last_name_ukr.$dirty && !$v.sailorInfo.last_name_ukr.maxLength)"
                    :text="$t('tooLongField')"
                  />
                  <ValidationAlert
                    v-else-if="$v.sailorInfo.last_name_ukr.$dirty && !$v.sailorInfo.last_name_ukr.alphaUA"
                    :text="$t('noAlphaUA')"
                  />
                </div>
                <div class="col-4">
                  <b-input
                    v-if="edit"
                    v-model="sailorInfo.first_name_ukr"
                    @blur="$v.sailorInfo.first_name_ukr.$touch()"
                    :placeholder="$t('name')"
                    type="text"
                    class="name form-control"
                  >
                  </b-input>
                  <ValidationAlert
                    v-if="$v.sailorInfo.first_name_ukr.$dirty && !$v.sailorInfo.first_name_ukr.required"
                    :text="$t('emptyField')"
                  />
                  <ValidationAlert
                    v-else-if="$v.sailorInfo.first_name_ukr.$dirty && !$v.sailorInfo.first_name_ukr.maxLength"
                    :text="$t('tooLongField')"
                  />
                  <ValidationAlert
                    v-else-if="$v.sailorInfo.first_name_ukr.$dirty && !$v.sailorInfo.first_name_ukr.alphaUA"
                    :text="$t('noAlphaUA')"
                  />
                </div>
                <div class="col-4">
                  <b-input
                    v-if="edit"
                    v-model="sailorInfo.middle_name_ukr"
                    @blur="$v.sailorInfo.middle_name_ukr.$touch()"
                    :placeholder="$t('middleName')"
                    type="text"
                    class="name form-control"
                  />
                  <ValidationAlert
                    v-if="$v.sailorInfo.middle_name_ukr.$dirty && !$v.sailorInfo.middle_name_ukr.maxLength"
                    :text="$t('tooLongField')"
                  />
                  <ValidationAlert
                    v-else-if="$v.sailorInfo.middle_name_ukr.$dirty && !$v.sailorInfo.middle_name_ukr.alphaUA"
                    :text="$t('noAlphaUA')"
                  />
                </div>
              </div>
              <div
                v-if="!edit"
                class="vx-row seafarerInfo-name"
                :class="{ 'pl-6': sailorInfo.exists_account, 'pl-1': !sailorInfo.exists_account }"
              >
                {{ sailorInfo.last_name_eng }} {{ sailorInfo.first_name_eng }}
              </div>
              <div
                v-if="edit"
                class="col-12 mt-1"
              >
                <label class="text-bold-300">
                  {{ $t('nameEN') }}
                </label>
              </div>
              <div class="flex-row-sb">
                <div class="col-6">
                  <b-input
                    v-if="edit"
                    v-model="sailorInfo.last_name_eng"
                    @blur="$v.sailorInfo.last_name_eng.$touch()"
                    :placeholder="$t('lastName')"
                    type="text"
                    class="name form-control"
                    >
                  </b-input>
                  <ValidationAlert
                    v-if="$v.sailorInfo.last_name_eng.$dirty && !$v.sailorInfo.last_name_eng.required"
                    :text="$t('emptyField')"
                  />
                  <ValidationAlert
                    v-else-if="$v.sailorInfo.last_name_eng.$dirty && !$v.sailorInfo.last_name_eng.maxLength"
                    :text="$t('tooLongField')"
                  />
                  <ValidationAlert
                    v-else-if="$v.sailorInfo.last_name_eng.$dirty && !$v.sailorInfo.last_name_eng.alphaEN"
                    :text="$t('noAlpha')"
                  />
                </div>
                <div class="col-6">
                  <b-input
                    v-if="edit"
                    v-model="sailorInfo.first_name_eng"
                    @blur="$v.sailorInfo.first_name_eng.$touch()"
                    :placeholder="$t('name')"
                    type="text"
                    class="name form-control"
                  >
                  </b-input>
                  <ValidationAlert
                    v-if="$v.sailorInfo.first_name_eng.$dirty && !$v.sailorInfo.first_name_eng.required"
                    :text="$t('emptyField')"
                  />
                  <ValidationAlert
                    v-else-if="$v.sailorInfo.first_name_eng.$dirty && !$v.sailorInfo.first_name_eng.maxLength"
                    :text="$t('tooLongField')"
                  />
                  <ValidationAlert
                    v-else-if="$v.sailorInfo.first_name_eng.$dirty && !$v.sailorInfo.first_name_eng.alphaEN"
                    :text="$t('noAlpha')"
                  />
                </div>
              </div>
              <div class="vx-row mt-1">
                <div class="seafarerInfo-item">
                  <label class="text-bold-300">
                    {{ $t('dateBorn') }}
                  </label>
                  <div
                    v-if="!edit"
                    class="date"
                  >
                    {{ sailorInfo.date_birth ? sailorInfo.date_birth.split('-').reverse().join('.') : '' }}
                  </div>
                  <b-input-group v-else>
                    <b-form-input
                      v-model="sailorInfo.date_birth"
                      @blur="$v.sailorInfo.date_birth.$touch()"
                      type="date"
                    />
                    <b-input-group-append>
                      <b-form-datepicker
                        v-model="sailorInfo.date_birth"
                        @hidden="$v.sailorInfo.date_birth.$touch()"
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
                    v-if="$v.sailorInfo.date_birth.$dirty && !$v.sailorInfo.date_birth.required && edit"
                    :text="$t('emptyField')"
                  />
                </div>
                <div class="seafarerInfo-item">
                  <label class="text-bold-300">
                    {{ $t('serialAndNum') }}
                  </label>
                  <div
                    v-if="!edit"
                    class="serial"
                  >
                    {{ sailorInfo.passport ? sailorInfo.passport.serial : '' }}
                  </div>
                  <b-input
                    v-else
                    v-model="sailorInfo.passport.serial"
                    @blur="$v.sailorInfo.passport.serial.$touch()"
                    :placeholder="$t('serialAndNum')"
                    type="text"
                    class="serial"
                  />
                  <ValidationAlert
                    v-if="$v.sailorInfo.passport.serial.$dirty && !$v.sailorInfo.passport.serial.required"
                    :text="$t('emptyField')"
                  />
                  <ValidationAlert
                    v-else-if="$v.sailorInfo.passport.serial.$dirty && !$v.sailorInfo.passport.serial.maxLength"
                    :text="$t('seriesLength')"
                  />
                </div>
                <div class="seafarerInfo-item">
                  <label class="text-bold-300">
                    {{ $t('taxNumber') }}
                  </label>
                  <div
                    v-if="!edit"
                    class="tax"
                  >
                    {{ sailorInfo.passport ? sailorInfo.passport.inn : '' }}
                  </div>
                  <b-input
                    v-else
                    v-model="sailorInfo.passport.inn"
                    @blur="$v.sailorInfo.passport.inn.$touch()"
                    :placeholder="$t('taxNumber')"
                    type="text"
                    class="tax"
                  />
                  <ValidationAlert
                    v-if="edit && $v.sailorInfo.passport.inn.$dirty && !$v.sailorInfo.passport.inn.required"
                    :text="$t('emptyField')"
                  />
                </div>
                <div class="seafarerInfo-item pr-1">
                  <label class="text-bold-300">
                    {{ $t('sex') }}
                  </label>
                  <div
                    v-if="!edit"
                    class="sex"
                  >
                    {{ sailorInfo.sex ? sailorInfo.sex[labelValue] : '' }}
                  </div>
                  <multiselect
                    v-else
                    v-model="sailorInfo.sex"
                    @close="$v.sailorInfo.sex.$touch()"
                    :searchable="true"
                    :preselectFirst="true"
                    :options="mappingSex"
                    :placeholder="$t('sex')"
                    :label="labelValue"
                    class="sex"
                    track-by="id"
                  />
                  <ValidationAlert
                    v-if="$v.sailorInfo.sex.$dirty && !$v.sailorInfo.sex.required && edit"
                    :text="$t('emptyField')"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div
        v-if="!mini"
        class="col-12 mt-2"
      >
        <div class="col-12 form-group text-left">
          <label class="text-bold-300">
            {{ $t('qualification') }} - {{ $t('rank') }}
          </label>
          <div class="rank">
            <span v-for="rank in sailorInfo.rank" :key="rank.id">
              {{ rank[labelName] }};
            </span>
          </div>
        </div>
        <div class="col-12 form-group text-left">
          <label class="text-bold-300">
            {{ $t('position') }}
          </label>
          <div class="position">
            <span v-for="position in sailorInfo.position" :key="position.id">
              {{ position[labelName] }};
            </span>
          </div>
        </div>
        <div class="col-12 form-group text-left">
          <label class="text-bold-300">
            {{ $t('financialPhoneNumber') }}
          </label>
          <div class="position">
            {{ sailorInfo.financial_phone }}
          </div>
        </div>
        <div class="flex-row-sb">
          <div class="col-6 form-group text-left">
            <label class="text-bold-300">
              {{ $t('phoneNumber') }}
            </label>
            <div class="flex-row">
              <div
                :key="phone"
                v-for="phone in sailorInfo.phoneList"
                class="mb-25 align-items-center d-flex"
              >
                <div class="pr-1">
                  {{ phone }}
                </div>
<!--                <div>-->
<!--                  <button-->
<!--                    v-if="!edit && !sailorInfo.exists_account"-->
<!--                    @click="registerSailorAccount(phone)"-->
<!--                    type="button"-->
<!--                    class="btn btn-outline-twitter"-->
<!--                    >-->
<!--                    {{ $t('registerPA') }}-->
<!--                  </button>-->
<!--                </div>-->
                <div>
                  <button
                    v-if="edit"
                    @click="updatePhoneList('delete', phone)"
                    type="button"
                    class="btn btn-outline-danger"
                  >
                    <trash-2-icon size="1.5x" class="custom-class"/>
                  </button>
                </div>
              </div>
            </div>
            <div class="flex-row-sb">
              <phone-mask-input
                v-if="edit"
                v-model.trim="sailorInfo.phoneNumber"
                @onBlur="$v.sailorInfo.phoneNumber.$touch()"
                placeholder="+38(050)123-12-13"
                class="w-full mainInfoPhone"
                id="mainInfoPhone"
              />
              <div
                v-if="edit"
                @click="updatePhoneList('add', sailorInfo.phoneNumber)"
              >
                <unicon
                  name="plus"
                  height="30px"
                  width="30px"
                  class="cursor add"
                />
              </div>
              <!--<ValidationAlert
                v-if="(sailorInfo.phoneNumber === '') && edit"
                :text="$t('phoneNumFormat')"
              />
              <ValidationAlert
                v-if="this.checkPhoneNumber && $v.sailorInfo.phoneNumber.$dirty && !$v.sailorInfo.phoneNumber.required && edit"
                :text="$t('emptyField')"
              />-->
              <ValidationAlert
                v-if="$v.sailorInfo.phoneNumber.$dirty && edit &&
                  (!$v.sailorInfo.phoneNumber.maxLength || !$v.sailorInfo.phoneNumber.minLength)"
                :text="$t('invalidPhoneNum')"
              />
            </div>
          </div>

        </div>
        <div class="flex-row-sb">
          <div class="col-6 form-group text-left">
            <label class="text-bold-300">
              {{ $t('email') }}
            </label>
            <div
              v-if="!edit"
              class="email"
            >
              {{ sailorInfo.email }}
            </div>
            <b-input
              v-else
              v-model.trim="sailorInfo.email"
              @blur="$v.sailorInfo.email.$touch()"
              :placeholder="$t('email')"
              type="text"
            />
            <ValidationAlert
              v-if="$v.sailorInfo.email.$dirty && !$v.sailorInfo.email.emailValid && edit"
              :text="$t('invalidEmail')"
            />
          </div>
        </div>
        <SailorsMerging v-if="!edit && checkAccess('sailors-merging')" />
      </div>
    </div>
  </b-form>
</template>

<script src="./SailorMainInfo.js"/>

<style lang="sass" scoped>
  @import '../../../assets/sass/seafarer/main'
</style>
