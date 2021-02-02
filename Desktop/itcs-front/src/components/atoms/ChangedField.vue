<template>
  <div>
    <div v-if="!row.item.old_obj_json">
      <label>{{ labelStringName }}:</label>
      {{ newValue }}
    </div>
    <div v-else class="pb-1">
      <label>{{ labelStringName }}:</label>
      <span
        v-if="oldValue && !newValue"
        class="deleted-record"
      >
        {{ oldValue }}
      </span>

      <span
        v-else-if="!oldValue && newValue"
        class="added-record"
      >
        {{ newValue }}
      </span>

      <span
        v-else-if="oldValue !== newValue"
        class="edited-record"
      >
        {{ oldValue }} &rarr; {{ newValue }}
          <!--<b-icon icon="arrow-right" class="ml-1 mr-1 text-white"/>-->
      </span>

      <span v-else-if="oldValue === newValue">
        {{ newValue }}
      </span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ChangedField',
  props: {
    row: Object,
    oldValue: [String, Number],
    newValue: [String, Number],
    labelName: [String]
  },
  data () {
    return {
      labelStringName: null
    }
  },
  mounted () {
    this.setLabelName()
  },
  methods: {
    setLabelName () {
      switch (this.labelName) {
        case 'country':
          if (this.row.item.content_type === 'passport') {
            this.labelStringName = this.$i18n.t('citizenship')
          } else {
            this.labelStringName = this.$i18n.t('country')
          }
          break
        case 'dateStart':
          switch (this.row.item.content_type) {
            case 'studentid':
              this.labelStringName = this.$i18n.t('dataEnrollment')
              break
            case 'lineinservicerecord':
              if (this.row.item.new_obj_json.record_type === 'Трудова книжка, довідка про фаховий стаж, ремонт, практику, тощо') {
                this.labelStringName = this.$i18n.t('periodStart')
              } else {
                this.labelStringName = this.$i18n.t('hireDate')
              }
              break
            case 'etiprofitpart':
            case 'etiregistry':
              this.labelStringName = this.$i18n.t('dateEffective')
              break
            default:
              this.labelStringName = this.$i18n.t('dateIssue')
          }
          break
        case 'dateEnd':
          switch (this.row.item.content_type) {
            case 'studentid':
              this.labelStringName = this.$i18n.t('dateEnd')
              break
            case 'lineinservicerecord':
              if (this.row.item.new_obj_json.record_type === 'Трудова книжка, довідка про фаховий стаж, ремонт, практику, тощо') {
                this.labelStringName = this.$i18n.t('periodEnd')
              } else {
                this.labelStringName = this.$i18n.t('fireDate')
              }
              break
            default:
              this.labelStringName = this.$i18n.t('dateTermination')
          }
          break
        case 'serial':
          if (this.row.item.content_type === 'passport') {
            this.labelStringName = this.$i18n.t('serialAndNum')
          } else {
            this.labelStringName = this.$i18n.t('serial')
          }
          break
        case 'dateMeeting':
          switch (this.row.item.content_type) {
            case 'statementadvancedtraining':
              this.labelStringName = this.$i18n.t('dateStartEdu')
              break
            case 'statemenetqualificationdocument':
            case 'sailorstatementdkk':
              this.labelStringName = this.$i18n.t('data_event')
              break
            case 'statementmedicalcertificate':
              this.labelStringName = this.$i18n.t('dateReceipt')
              break
            default:
              this.labelStringName = this.$i18n.t('meetingDate')
          }
          break
        case 'dateEndMeeting':
          if (this.row.item.content_type === 'statementadvancedtraining') {
            this.labelStringName = this.$i18n.t('dateEndEdu')
          } else {
            this.labelStringName = this.$i18n.t('dateEndEvent')
          }
          break
        default:
          this.labelStringName = this.$i18n.t(`${this.labelName}`)
      }
    }
  }
}
</script>
