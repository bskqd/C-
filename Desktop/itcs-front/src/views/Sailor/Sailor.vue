<template>
  <div class="seafarerTabs sailorProfilePage">
    <b-card no-body v-if="checkAccess('menuItem-sailor')" class="mt-0">
      <SailorMainInfo ref="mainInfo"/>
    </b-card>

    <SailorContractUploading v-if="isContractNeeded" />

    <b-card v-else-if="!isContractNeeded" no-body>
      <b-tabs fill pills>
        <TabsList
          v-if="checkAccess('tab-sailorPassport') || checkAccess('tab-civilPassport') ||
           checkAccess('tab-fullNameChanges') || checkAccess('tab-sailorPassportStatement')"
          link="passports-sailors"
          icon="passports"
          countDocKey="passportAll"
          labelKey="passports"
          :tabs="tabPassport"
          :childPermissions="[checkAccess('tab-sailorPassport'), checkAccess('tab-civilPassport'),
           checkAccess('tab-fullNameChanges'), checkAccess('tab-sailorPassportStatement')]"/>

        <TabsList
          v-if="checkAccess('tab-education') || checkAccess('tab-student') || checkAccess('tab-educationStatement')"
          link="education-documents"
          icon="graduation"
          countDocKey="educationAll"
          labelKey="education"
          :tabs="tabEducation"
          :childPermissions="[checkAccess('tab-education'), checkAccess('tab-student'), checkAccess('tab-educationStatement')]"/>

        <TabsList
          v-if="checkAccess('tab-qualification') || checkAccess('tab-qualificationStatement')"
          link="qualification-documents"
          icon="qualification"
          countDocKey="qualificationAll"
          labelKey="qualificationDocsTab"
          :tabs="tabQualification"
          :childPermissions="[checkAccess('tab-qualification'), checkAccess('tab-qualificationStatement')]"/>

        <TabsList
          v-if="checkAccess('tab-etiCertificate') || checkAccess('tab-etiStatement')"
          link="certification-certificates"
          icon="ntzcerts"
          countDocKey="certificateAll"
          labelKey="eti"
          :tabs="tabCertification"
          :childPermissions="[checkAccess('tab-etiCertificate'), checkAccess('tab-etiStatement')]"/>

        <TabsList
          v-if="checkAccess('tab-serviceRecordBook') || checkAccess('tab-experience') || checkAccess('tab-serviceRecordStatement')"
          link="experience-records"
          icon="experience"
          countDocKey="experienceAll"
          labelKey="experience"
          :tabs="tabExperience"
          :childPermissions="[checkAccess('tab-serviceRecordBook'), checkAccess('tab-experience'), checkAccess('tab-serviceRecordStatement')]"/>

        <TabsList
          v-if="checkAccess('tab-sqcProtocol') || checkAccess('tab-sqcStatement') || checkAccess('tab-sqcWishes')"
          :link="checkAccess('tab-sqcStatement') ? 'sqc-statements' : 'sqc-protocols'"
          icon="dcc"
          countDocKey="sqcAll"
          labelKey="sqc"
          :tabs="tabSQC"
          :childPermissions="[checkAccess('tab-sqcStatement'), checkAccess('tab-sqcProtocol'), checkAccess('tab-sqcWishes')]"/>

        <TabsList
          v-if="checkAccess('tab-medical') || checkAccess('tab-medicalStatement')"
          link="medical-certificates"
          icon="medical"
          countDocKey="medicalAll"
          labelKey="medical"
          :tabs="tabMedicine"
          :childPermissions="[checkAccess('tab-medical'), checkAccess('tab-medicalStatement')]"/>

        <TabsList
          v-if="checkAccess('tab-positionStatement')"
          link="position-statements"
          icon="positionStatement"
          countDocKey="positionStatement"
          labelKey="position" />

      </b-tabs>
    </b-card>

    <b-card v-if="!isContractNeeded" no-body>
      <router-view></router-view>
    </b-card>

    <b-card v-if="checkAccess('menuItem-agentInfo')" no-body>
      <SailorAgentInfo />
    </b-card>

<!--    <b-card v-if="viewWebCam || registerCode.status || signatureKey.status" class="camera-card" no-body>-->
<!--&lt;!&ndash;      <WebCam v-if="viewWebCam" />&ndash;&gt;-->
<!--      {{ registerCode }}-->
<!--      <div-->
<!--        v-if="registerCode.status"-->
<!--        class="mt-4 pt-4 p-2"-->
<!--      >-->
<!--        <div class="d-flex justify-content-flex-end">-->
<!--          <unicon-->
<!--            @click="closeRegisterCord"-->
<!--            name="multiply"-->
<!--            height="15px"-->
<!--            width="15px"-->
<!--            class="cursor delete"-->
<!--          />-->
<!--        </div>-->
<!--        <h4 class="text-left">{{ $t('setCode') }}</h4>-->
<!--        <b-input-->
<!--            v-model="code"-->
<!--            class="form-control"-->
<!--          >-->
<!--          </b-input>-->
<!--          <b-button-->
<!--            @click="codeRegistration(code)"-->
<!--            class="mt-1"-->
<!--            type="button"-->
<!--            variant="success"-->
<!--          >-->
<!--            {{ $t('save') }}-->
<!--          </b-button>-->
<!--      </div>-->
<!--&lt;!&ndash;      <SignatureKey v-if="signatureKey" />&ndash;&gt;-->
<!--    </b-card>-->
  </div>
</template>

<script src="./Sailor.js"/>

<style lang="sass">
  @import '../../assets/sass/seafarer/main'
</style>
