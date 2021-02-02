<template>
  <div class="pageList">
    <div class="w-50">
      <b>{{ $t('login') }} *</b>
      <multiselect
        v-model="dataForm.login"
        @close="$v.dataForm.login.$touch()"
        :searchable="true"
        :options="mappingLogin"
        label="username"
        track-by="id"
      />
      <ValidationAlert
        v-if="$v.dataForm.login.$dirty && !$v.dataForm.login.required"
        :text="$t('emptyField')"
      />
      <div>
        {{ dataForm.login ? `${dataForm.login.last_name} ${dataForm.login.first_name}` : '' }}
      </div>
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
          @click="checkUserInfo"
          variant="success"
          class="mt-1"
        >
        {{ $t('addKey') }}
      </b-button>
      </b-overlay>
    </div>
  </div>
</template>

<script src="./AddUbikeyToLogin.js"/>
