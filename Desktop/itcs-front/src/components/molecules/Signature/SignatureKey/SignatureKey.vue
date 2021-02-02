<template>
  <div class="mt-2">
    <div class="flex-row-sb mb-1 col-12">
      <div>
        <label>{{ $t('ecp') }}</label>
      </div>
      <div>
        <unicon
          @click="closeSignatureKey"
          name="multiply"
          height="15px"
          width="15px"
          class="cursor delete"
        />
      </div>
    </div>
    <div
      v-if="(!this.$parent.$refs.protocolsSQC.$refs.protocolSQCInfo.$refs.signature.loadKey && signatureKey.signAccess) ||
        (!this.$parent.$refs.protocolsSQC.$refs.protocolSQCInfo.$refs.signature.loadStamp && permissionWriteStamp)"
      class="d-flex flex-column text-center"
    >
      <div class="p-1">
        <span>{{ $t('server') }}</span>
        <multiselect
          v-model="server"
          :options="serverOptions"
          :placeholder="$t('server')"
          :allow-empty="false"
          :searchable="true"
          label="issuerCNs"
          track-by="cmpAddress"
        />
      </div>

      <div
        v-if="signatureKey.signAccess"
        class="p-1"
      >
        <b-form-file
          v-model="fileSign"
          @input="checkFileNameSign()"
          :placeholder="$t('loadKey')"
          :browse-text="$t('browse')"
          accept=".ZS2, .JKS"
        />
      </div>
      <small
        v-if="errorFileSign"
        class="required-field-star">{{ $t('errorFileSign') }}</small>
      <div
        v-if="signatureKey.signAccess"
        class="p-1"
      >
        <b-input
          v-model="passwordSign"
          :placeholder="$t('password')"
          type="password"
        />
      </div>

      <div
        v-if="permissionSuperAdmin || permissionWriteStamp"
        class="p-1"
      >
        <b-form-file
          v-model="fileStamp"
          @input="checkFileNameStamp()"
          :placeholder="$t('loadStamp')"
          :browse-text="$t('browse')"
          accept=".ZS2, .JKS"
        />
      </div>
      <small v-if="errorFileStamp" class="required-field-star">{{ $t('errorFileStamp') }}</small>
      <div
        v-if="permissionSuperAdmin || permissionWriteStamp"
        class="p-1"
      >
        <b-input
          v-model="passwordStamp"
          :placeholder="$t('password')"
          type="password"
        />
      </div>

      <div class="p-1">
        <b-button
          @click="readKeyFile"
          :disabled="!passwordSign || !fileSign || (permissionWriteStamp && (!fileStamp || !passwordStamp)) || !server"
          class="col-4 mt-2"
        >
          {{ $t('farther') }}
        </b-button>
      </div>
    </div>
    <div
      v-if="this.$parent.$refs.protocolsSQC.$refs.protocolSQCInfo.$refs.signature.loadKey"
      class="text-left p-2"
    >
      <div class="pb-1 text-center">
        <span>{{ $t('infoKey') }}: </span>
      </div>
      <div class="pb-1">
        <span>{{ $t('name') }}: </span>
        <span>{{ this.$parent.$refs.protocolsSQC.$refs.protocolSQCInfo.$refs.signature.signatureDataSign.subjCN }}</span>
      </div>
      <div class="pb-1">
        <span>{{ $t('position') }}: </span>
        <span>{{ this.$parent.$refs.protocolsSQC.$refs.protocolSQCInfo.$refs.signature.signatureDataSign.subjTitle }}</span>
      </div>
      <div class="pb-1">
        <span>{{ $t('email') }}: </span>
        <span>{{ this.$parent.$refs.protocolsSQC.$refs.protocolSQCInfo.$refs.signature.signatureDataSign.subjEMail }}</span>
      </div>
      <div class="pb-1">
        <span>{{ $t('city') }}: </span>
        <span>{{ this.$parent.$refs.protocolsSQC.$refs.protocolSQCInfo.$refs.signature.signatureDataSign.subjLocality }}</span>
      </div>
      <div class="pb-1">
        <span>{{ $t('name') }}: </span>
        <span>{{ this.$parent.$refs.protocolsSQC.$refs.protocolSQCInfo.$refs.signature.signatureDataSign.subjOrg }}</span>
      </div>
    </div>
    <div
      v-if="this.$parent.$refs.protocolsSQC.$refs.protocolSQCInfo.$refs.signature.loadStamp"
      class="text-left p-2"
    >
      <div class="pb-1 text-center">
        <span>{{ $t('infoStamp') }}: </span>
      </div>
      <div class="pb-1">
        <span>{{ $t('name') }}: </span>
        <span>{{ this.$parent.$refs.protocolsSQC.$refs.protocolSQCInfo.$refs.signature.signatureDataStamp.subjCN }}</span>
      </div>
      <div class="pb-1">
        <span>{{ $t('email') }}: </span>
        <span>{{ this.$parent.$refs.protocolsSQC.$refs.protocolSQCInfo.$refs.signature.signatureDataStamp.subjEMail }}</span>
      </div>
      <div class="pb-1">
        <span>{{ $t('city') }}: </span>
        <span>{{ this.$parent.$refs.protocolsSQC.$refs.protocolSQCInfo.$refs.signature.signatureDataStamp.subjLocality }}</span>
      </div>
      <div class="pb-1">
        <span>{{ $t('name') }}: </span>
        <span>{{ this.$parent.$refs.protocolsSQC.$refs.protocolSQCInfo.$refs.signature.signatureDataStamp.subjOrg }}</span>
      </div>
    </div>
    <div
      v-if="(this.$parent.$refs.protocolsSQC.$refs.protocolSQCInfo.$refs.signature.loadKey && signatureKey.signAccess) ||
        (this.$parent.$refs.protocolsSQC.$refs.protocolSQCInfo.$refs.signature.loadStamp && permissionWriteStamp)"
    >
      <div class="text-center">
        <b-button
          @click="signDocFile"
          :disabled="(!this.$parent.$refs.protocolsSQC.$refs.protocolSQCInfo.$refs.signature.loadKey &&
            signatureKey.signAccess) ||
            (!this.$parent.$refs.protocolsSQC.$refs.protocolSQCInfo.$refs.signature.loadStamp && permissionWriteStamp)"
          class="col-6"
        >{{ $t('setSign') }}</b-button>
      </div>
      <div class="text-center pt-2">
        <b-button
          @click="goBackSign"
          class="btn col-6">{{ $t('back') }}</b-button>
      </div>
    </div>

  </div>
</template>

<script src="./SignatureKey.js"></script>
