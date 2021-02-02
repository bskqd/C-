<template>
  <div>
    <b-overlay
      :show="signatureButtonLoader"
      spinner-variant="primary"
      opacity="0.65"
      blur="2px"
      variant="white"
      class="w-100"
      spinner-small
    >
      <b-button
        @click="setSignature()"
        variant="success"
      >
        {{ $t('setSign') }}
      </b-button>
    </b-overlay>
  </div>
</template>

<script src="./Signature.js"></script>
