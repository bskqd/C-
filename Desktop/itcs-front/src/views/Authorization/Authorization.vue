<template>
  <div class="authpage">
    <title>{{ $t('authorization') }}</title>
    <div v-if="selfHost" class="authpage-logo">
      <unicon name="logoMain" fill="#000" height="50px" width="50px"/>
    </div>
    <div
      v-if="!firsAuth"
      :class="{'flex-column': !selfHost}"
      class="authpage-form"
    >
        <div v-if="selfHost" class="authpage-form--left">
          <img src="@/assets/images/auth/auth-step1.jpg" alt="">
        </div>
        <div
          v-else
          class="authpage-form--left"
          :class="{'w-100 p-1 mb-2': !selfHost}"
          :style="{'background: #133370': !selfHost}"
        >
          <img src="@/assets/img/logo5.svg" alt="">
        </div>

      <div
        class="authpage-form--right"
        :class="{'w-100': !selfHost}"
      >
          <form action="">
            <div class="right--title">{{ $t('authorization') }} </div>
            <label class="text-bold-600" for="setLogin">{{ $t('login') }}</label>
            <input type="text" class="form-control" id="setLogin" v-model="login" placeholder="">
            <label class="text-bold-600" for="setPass">{{ $t('pass') }}</label>
            <input type="password" class="form-control" id="setPass" v-model="pass" @keyup.enter="setLogin()">
            <button
              @click="setLogin()"
              type="button"
              class="btn"
            >
              {{ $t('sign') }}
            </button>
            <div class="row">
              <div class="col-lg-12 mb-1">
                <span type="text" v-if="noAccount" class="danger">{{ $t('noAccount') }}</span>
              </div>
            </div>
          </form>
        </div>
    </div>
    <div v-if="firsAuth" class="authpage-form justify-content-center">
      <b-form @submit.prevent="checkNewPass">
        <div class="mt-1 mb-1">
          <h5 class="right--title">{{ $t('changePassword') }} </h5>
          <small class="pb-1">{{ $t('passwordRegexp') }}</small>
        </div>

        <div class="position-relative">
          <label class="text-bold-600" :for="passOld">{{ $t('passwordOlt') }}</label>
          <b-input
            v-model="passOld"
            @blur="$v.passOld.$touch()"
            class="form-control mb-1"
            type="password"/>
          <ValidationAlert
            v-if="$v.passOld.$dirty && !$v.passOld.required"
            :text="$t('emptyField')"
          />
        </div>

        <div class="position-relative">
          <label class="text-bold-600" :for="passNew">{{ $t('passwordNew') }}</label>
          <b-input
            v-model="passNew"
            @blur="$v.passNew.$touch()"
            class="form-control mb-1"
            type="password"
            />
          <ValidationAlert
            v-if="$v.passNew.$dirty && !$v.passNew.required"
            :text="$t('emptyField')"
          />
          <ValidationAlert
            v-else-if="$v.passNew.$dirty && !$v.passNew.pass"
            :text="$t('passwordRegexp')"
          />
          <ValidationAlert
            v-else-if="$v.passNew.$dirty && !$v.passNew.minLength"
            :text="$t('passMinLength')"
          />
        </div>

        <div class="position-relative">
          <label class="text-bold-600" :for="passNewRepeat">{{ $t('passwordNewRepeat') }}</label>
          <b-input
            v-model="passNewRepeat"
            @blur="$v.passNewRepeat.$touch()"
            @keyup.enter="checkNewPass()"
            class="form-control"
            type="password"/>
          <ValidationAlert
            v-if="$v.passNewRepeat.$dirty && !$v.passNewRepeat.required"
            :text="$t('emptyField')"
          />
        </div>

        <b-button type="submit" variant="success" class="btn mt-1">{{ $t('save') }}</b-button>
        <div class="row">
          <div v-if="errorOldPass" class="col-lg-12 mb-1 danger">
            {{ $t('errorOldPass') }}
          </div>
          <div v-if="errorNewPass" class="col-lg-12 mb-1 danger">
            {{ $t('errorNewPass') }}
          </div>
        </div>
      </b-form>
    </div>
  </div>
</template>

<script src="./Authorization.js" />
<style lang="sass">
  @import '../../assets/sass/auth'
  @import '../../assets/sass/main'
</style>
