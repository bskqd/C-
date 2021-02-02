<template>
  <div class="main">
    <div
      v-if="checkAccess('main-agent')"
      class="card mt-0"
    >
      <div class="p-1">
        <img
          :src="agentQR"
          width="200px"
        >
      </div>
      <div class="m-2 d-flex justify-content-between">
        <div>{{ $t('agentId') }}: {{ userInfo.id }}</div>
        <b-button
          v-clipboard="() => linkForSailor"
          v-clipboard:success="clipboardSuccessHandler"
          class="w-20"
        >{{ $t('copy') }}</b-button>
      </div>
      <div hidden class="pb-2">
        <h4>{{ $t('addSailorByNumber') }}:</h4>
        <div class="d-flex justify-content-center">
          <the-mask
            v-if="!codeSent"
            v-model="sailorPhone"
            mask="+380FT-TTT-TT-TT"
            :tokens="phoneNumberRegexp"
            class="form-control w-20"
            placeholder="+38 000 000 00 00"/>
          <ValidationAlert
            v-if="$v.sailorPhone.$dirty && !$v.sailorPhone.required"
            :text="$t('emptyField')"
          />
          <ValidationAlert
            v-else-if="$v.sailorPhone.$dirty && (!$v.sailorPhone.maxLength || !$v.sailorPhone.minLength)"
            :text="$t('invalidPhoneNum')"
          />
          <the-mask
            v-if="codeSent"
            v-model="code"
            mask="TTTT"
            :tokens="phoneNumberRegexp"
            class="form-control w-20"
            placeholder="0000"/>
          <ValidationAlert
            v-if="$v.code.$dirty && !$v.code.required"
            :text="$t('emptyField')"
          />
          <ValidationAlert
            v-else-if="$v.code.$dirty && (!$v.code.maxLength || !$v.code.minLength)"
            :text="$t('invalidCode')"
          />
          <b-button
            @click="validateForm(codeSent ? 'confirm' : 'code')"
            class="w-10 p-25 ml-2"
          >{{ codeSent ? $t('confirm') : $t('send') }}</b-button>
          <b-button
            v-if="codeSent"
            @click="sendCode('resendCode')"
            :disabled="!!timeLeft"
            class="cursor-pointer no-btn">
            {{ timeLeft ? $t('timeLeft') + timeLeft : $t('canResendCode') }}
          </b-button>
        </div>
      </div>
    </div>
    <router-link
      v-if="checkAccess('main-addSailor')"
      :to="{ name: 'new-sailor' }"
      replace
    >
      <div class="vx-card vx-card-plus p-3">
         <plus-circle-icon
          size="1.5x"
          class="custom-class 123"
        />
      </div>
    </router-link>
    <MainSailorHistory v-if="checkAccess('main-sailorsList')"/>
    <MainAgentHistory v-else/>
  </div>
</template>

<script src="./Main.js"/>

<style>
  .no-btn, .no-btn:disabled {
    border: none;
    margin-left: 5px;
    background: none;
    text-align: left;
    color: #475f7b;
  }
  .no-btn:hover, .no-btn:active, .no-btn:focus {
    color: #475f7b !important;
    background: none !important;
  }
</style>
