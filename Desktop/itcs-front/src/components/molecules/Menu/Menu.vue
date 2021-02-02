<template>
  <div>
    <div
      slot="header"
      class="header-sidebar vx-logo cursor-pointer"
    >
        <router-link
            class="w-full d-flex align-items-center"
            to="/"
          >
          <div v-if="selfHost" class="d-flex align-items-center">
            <unicon name="logo" fill="#000" height="50px" width="50px"></unicon>
            <span class="vx-logo-text text-primary ml-3">
              MARAD
            </span>
          </div>
          <div v-else>
            <img src="@/assets/img/logo5.svg" alt="logo">
          </div>
        </router-link>
    </div>

    <section
      class="ps-container scroll-area-v-nav-menu pt-2 ps ps--theme_default ps--active-y"
      data-ps-id="dd35157a-f86c-c9c3-e24d-cb6e2d39bd9a"
    >
      <span class="navigation-header truncate">
        {{ $t('main') }}
      </span>
      <ul
        class="pl-1 pr-1"
        data-menu="menu-navigation"
        data-icon-style="lines"
      >
      <ListItem
        v-if="checkAccess('menuItem-sailor')"
        :activePage="active === 'home'"
        routingLink="/"
        labelKey="sailor"
        icon="home-icon"/>
      </ul>
      <span
        v-if="checkAccess('menuLabel-documents')"
        class="navigation-header truncate">
        {{ $t('documents') }}
      </span>
      <ul
        class="pl-1 pr-1"
        data-menu="menu-navigation"
        data-icon-style="lines"
      >
<!--        НОВЫЙ-->
        <ListItem
          v-if="checkAccess('menuItem-statementSQC')"
          :activePage="active === 'statementSQC'"
          :notify="userNotification.statement_dkk_aproved + userNotification.statement_dkk_processing + userNotification.statement_dkk_from_personal_cabinet"
          routingLink="/statement/sqc/approved"
          labelKey="statementSQC"
          icon="circle-icon" />

        <ListItem
          v-if="checkAccess('tab-statementServiceRecordBook')"
          :activePage="active === 'statementSRB'"
          :notify="userNotification.statement_service_record"
          routingLink="/statement/srb/all"
          labelKey="recordBookStatement"
          icon="check-circle-icon" />

        <ListItem
          v-if="checkAccess('menuItem-statementETI')"
          :activePage="active === 'statementETI'"
          routingLink="/eti-statements"
          labelKey="etiStatementReport"
          icon="check-circle-icon" />

        <ListItem
          v-if="checkAccess('menuItem-statementAdvanceTraining')"
          :activePage="active === 'statementAdvanceTraining'"
          routingLink="/advance-training-statements"
          labelKey="advanceTrainingStatement"
          icon="check-circle-icon" />

        <ListItem
          v-if="checkAccess('menuItem-etiPayments')"
          :activePage="active === 'etiPayments'"
          routingLink="/eti-payments"
          labelKey="etiPayments"
          icon="check-circle-icon" />

        <!--<ListItem
          v-if="checkAccess('menuItem-postVerificationDocuments')"
          :activePage="active === 'processingDoc'"
          routingLink="/processing-documents"
          labelKey="processingDoc"
          icon="check-circle-icon" />-->

        <ListItem
          v-if="checkAccess('menuItem-agentVerification')"
          :activePage="active === 'agentsDocument'"
          routingLink="/agent-verification"
          labelKey="agentDocsVerification"
          icon="check-circle-icon" />

        <ListItem
          v-if="checkAccess('menuItem-verificationAccount')"
          :activePage="active === 'newAccounts'"
          :notify="userNotification.user_to_verificate"
          routingLink="/new-accounts"
          labelKey="verificationAcc"
          icon="check-circle-icon" />

        <!--<ListItem
          v-if="checkAccess('menuItem-documentsToSign')"
          :activePage="active === 'documentSign'"
          :notify="userNotification.document_to_sign"
          routingLink="/documents-to-sign"
          labelKey="documentsToSign"
          icon="check-circle-icon" />-->

        <ListItem
          v-if="checkAccess('menuItem-qualificationPackageStatement')"
          :activePage="active === 'qualificationPackageStatement'"
          routingLink="/package-qualification-statement"
          labelKey="packageQualificationStatements"
          icon="check-circle-icon" />

<!--        <li-->
<!--          v-if="checkAccess('menuItem-report')"-->
<!--          :class="{active: report}"-->
<!--          @click="reportView = !reportView"-->
<!--          class="vs-sidebar&#45;&#45;item"-->
<!--        >-->
<!--          <router-link-->
<!--            class="flex-row-normal"-->
<!--            to=""-->
<!--            replace-->
<!--          >-->
<!--            <span>-->
<!--              <file-text-icon-->
<!--                size="1.5x"-->
<!--                class="custom-class"-->
<!--              />-->
<!--              {{ $t('report') }}-->
<!--            </span>-->
<!--          </router-link>-->
<!--        </li>-->
        <ListItem
          v-if="checkAccess('menuItem-report')"
          :activePage="active === 'report'"
          :child="false"
          routingLink="/report/sqc"
          labelKey="report"
          icon="circle-icon" />

<!--        <ListItem-->
<!--          v-if="checkAccess('admin')"-->
<!--          :activePage="active === 'reportBO'"-->
<!--          :child="false"-->
<!--          routingLink="/report/debtor"-->
<!--          labelKey="reportBO"-->
<!--          icon="circle-icon" />-->

<!--        <ListItem-->
<!--          v-if="checkAccess('menuItem-upload')"-->
<!--          :activePage="active === 'uploadDocs'"-->
<!--          routingLink="/upload-documents"-->
<!--          labelKey="uploadDocs"-->
<!--          icon="upload-icon" />-->

        <ListItem
          v-if="checkAccess('menuItem-userHistory')"
          :activePage="active === 'userHistory'"
          routingLink="/user-history"
          labelKey="userHistory"
          icon="archive-icon" />
      </ul>

      <span
        v-if="checkAccess('menuLabel-admin')"
        class="navigation-header truncate"
      >
        {{ $t('admin') }}
      </span>
      <ul
        class="pl-1 pr-1"
        data-menu="menu-navigation"
        data-icon-style="lines"
      >
        <ListItem
          v-if="checkAccess('menuItem-backOffice')"
          :activePage="active === 'backOffice'"
          routingLink="/back-office/coefficients"
          labelKey="backOffice"
          icon="circle-icon" />

<!--        <ListItem-->
<!--          v-if="checkAccess('menuItem-etiCourse')"-->
<!--          :activePage="coursesETI"-->
<!--          routingLink="/back-office/courses-eti"-->
<!--          labelKey="coursesETI"-->
<!--          icon="check-circle-icon" />-->

<!--        <ListItem-->
<!--          v-if="checkAccess('menuItem-priceEtiCourse')"-->
<!--          :activePage="profitPartETI"-->
<!--          routingLink="/back-office/course-price-ETI"-->
<!--          labelKey="coursePriceETI"-->
<!--          icon="check-circle-icon" />-->

<!--        <ListItem-->
<!--          v-if="checkAccess('menuItem-pricePacket')"-->
<!--          :activePage="priceETI"-->
<!--          routingLink="/back-office/price-eti"-->
<!--          labelKey="priceETI"-->
<!--          icon="dollar-sign-icon" />-->

        <ListItem
          v-if="checkAccess('menuItem-agentsStatement')"
          :activePage="active === 'newAgents'"
          :notify="userNotification.statement_agent"
          routingLink="/agent-statement"
          labelKey="agentStatement"
          icon="check-circle-icon" />

        <ListItem
          v-if="checkAccess('menuItem-agentsStatementFromSailor')"
          :activePage="active === 'agentStatements'"
          :notify="userNotification.statement_agent_sailor"
          routingLink="/agent-statement-from-sailor"
          :labelKey="checkAccess('marad') ? 'contractInProcessing' : 'agentStatementFromSailor'"
          icon="check-circle-icon" />

<!--        <ListItem-->
<!--          v-if="checkAccess('menuItem-etiInstitution')"-->
<!--          :activePage="ETI"-->
<!--          routingLink="/back-office/list-eti"-->
<!--          labelKey="listETI"-->
<!--          icon="check-circle-icon" />-->

<!--        <ListItem-->
<!--          v-if="checkAccess('menuItem-etiDealing')"-->
<!--          :activePage="dealingETI"-->
<!--          routingLink="/back-office/dealing"-->
<!--          labelKey="dealingETI"-->
<!--          icon="check-circle-icon" />-->

<!--        <ListItem-->
<!--          v-if="checkAccess('menuItem-agents')"-->
<!--          :activePage="agentGroups"-->
<!--          :labelKey="permissionReadAgentGroups ? 'agentGroups' : 'myAgents'"-->
<!--          routingLink="/back-office/agent-groups"-->
<!--          icon="check-circle-icon" />-->
      </ul>

      <span
        v-if="checkAccess('menuLabel-settings')"
        class="navigation-header truncate"
      >
        {{ $t('settings') }}
      </span>
      <ul
        class="pl-1 pr-1"
        data-menu="menu-navigation"
        data-icon-style="lines"
      >
        <ListItem
          v-if="checkAccess('menuItem-newUser')"
          :activePage="active === 'userRegistration'"
          routingLink="/registration"
          labelKey="registration"
          icon="plus-square-icon" />

        <ListItem
          v-if="checkAccess('admin')"
          :activePage="active === 'directory'"
          routingLink="/directory/address"
          labelKey="directory"
          icon="book-icon" />

<!--        <ListItem-->
<!--          v-if="checkAccess('admin') && directory"-->
<!--          :activePage="address"-->
<!--          :child="true"-->
<!--          routingLink="/directory/address"-->
<!--          labelKey="address"-->
<!--          icon="circle-icon" />-->
      </ul>
    </section>
    <div style="display: none">{{ version }}</div>
  </div>
</template>

<script src="./Menu.js"/>

<style lang="scss">
  @import '../../../assets/scss/vuexy/components/verticalNavMenu';
</style>
