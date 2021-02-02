<template>
  <b-form @submit.prevent="checkInfo">
    <template #header>
      <div class="flex-row-sb">
        <div class="text-uppercase">
          {{ $t('addProtocolSQC') }}
        </div>
        <unicon
          @click="newDoc = !newDoc"
          name="multiply"
          fill="#42627e"
          height="25px"
          width="25px"
          class="close"
        />
      </div>
    </template>
    <div class="text-left">
      <div class="flex-row-sb form-group">
        <div class="col-12">
          <label>
            {{ $t('approvedStatements') }}
            <span class="requaredFieldStar">*</span>
          </label>
          <multiselect
            v-model="dataForm.approvedApplications"
            @close="$v.dataForm.approvedApplications.$touch()"
            :options="approvedApplications"
            :searchable="true"
            :placeholder="$t('approvedStatements')"
            label="number"
            track-by="id"
          >
            <span slot="noOptions">
              {{ $t('notFind') }}
            </span>
          </multiselect>
          <ValidationAlert
            v-if="$v.dataForm.approvedApplications.$dirty && !$v.dataForm.approvedApplications.required"
            :text="$t('emptyField')"
          />
        </div>
      </div>

      <div class="flex-row-sb form-group mt-2">
        <div class="col-6">
          <label>
            {{ $t('dateOfThe') }}
            <span class="requaredFieldStar">*</span>
          </label>
          <b-input-group>
            <b-form-input
              v-model="dataForm.dateMeeting"
              @blur="$v.dateMeetingObject.$touch()"
              type="date"
            />
            <b-input-group-append>
              <b-form-datepicker
                v-model="dataForm.dateMeeting"
                @hidden="$v.dateMeetingObject.$touch()"
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
            v-if="$v.dateMeetingObject.$dirty && !$v.dateMeetingObject.required"
            :text="$t('emptyField')"
          />
          <ValidationAlert
            v-else-if="$v.dateMeetingObject.$dirty && (!$v.dateMeetingObject.minValue || !$v.dateMeetingObject.maxValue)"
            :text="$t('dateIssuedValid')"
          />
        </div>
        <div class="col-6">
          <label>
            {{ $t('headCommission') }}
            <span class="requaredFieldStar">*</span>
          </label>
          <multiselect
            v-model="dataForm.headCommission"
            @close="$v.dataForm.headCommission.$touch()"
            :options="commission"
            :searchable="true"
            :placeholder="$t('headCommission')"
            label="name"
            track-by="id"
          />
          <ValidationAlert
            v-if="$v.dataForm.headCommission.$dirty && !$v.dataForm.headCommission.required"
            :text="$t('emptyField')"
          />
        </div>
      </div>
      <div class="flex-row-sb form-group mt-2">
        <div class="col-12">
          <label>
            {{ $t('membersCommission') }}
            <span class="requaredFieldStar">*</span>
          </label>
          <multiselect
            v-model="dataForm.membersCommission"
            @close="$v.dataForm.membersCommission.$touch()"
            :options="commissionMembers"
            :searchable="true"
            :multiple="true"
            :placeholder="$t('membersCommission')"
            label="name"
            track-by="id"
          >
            <span slot="noOptions">
              {{ $t('selectCommission') }}
            </span>
          </multiselect>
          <ValidationAlert
            v-if="$v.dataForm.membersCommission.$dirty && !$v.dataForm.membersCommission.required"
            :text="$t('emptyField')"
          />
          <ValidationAlert
            v-else-if="$v.dataForm.membersCommission.$dirty && (!$v.dataForm.membersCommission.length.minValue ||
             !$v.dataForm.membersCommission.length.maxValue)"
            :text="$t('invalidCommissionCount')"
          />
        </div>
      </div>
      <div class="flex-row-sb form-group mt-2">
        <div class="col-12">
          <label>
            {{ $t('solution') }}
            <span class="requaredFieldStar">*</span>
          </label>
          <multiselect
            v-model="dataForm.decision"
            @close="$v.dataForm.decision.$touch()"
            :options="solutions"
            :searchable="true"
            :placeholder="$t('solution')"
            :label="labelName"
            track-by="id"
          />
          <ValidationAlert
            v-if="$v.dataForm.decision.$dirty && !$v.dataForm.decision.required"
            :text="$t('emptyField')"
          />
        </div>
      </div>
      <div class="col-12">
        <FileDropZone ref="mediaContent" />
      </div>
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
        class="mt-1"
        type="submit"
        variant="success"
      >
        {{ $t('save') }}
      </b-button>
    </b-overlay>
  </b-form>
</template>

<script src="./SailorSQCProtocolsAdd.js" />

<style scoped>

</style>
