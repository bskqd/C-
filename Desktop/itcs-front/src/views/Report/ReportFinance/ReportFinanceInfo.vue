<template>
  <b-card header-tag="header">
    <template #header>
      <div class="flex-row-sb">
        <div class="text-uppercase">
          {{ $t('viewReportRecord') }}
        </div>
        <unicon
          @click="hideDetailed(row)"
          name="multiply"
          fill="#42627e"
          height="20px"
          width="20px"
          class="close"
        />
      </div>
    </template>
    <div class="seafarerInfoList text-left">
      <b class="w-100 mb-0">{{ $t('firstForm') }}:</b>
      <div>
        {{ $t('price') }} {{ $t('secondForm') }} : {{ row.item.price_form1 }}
      </div>
      <div>
        {{ $t('total') }} {{ $t('secondForm') }} : {{ row.item.sum_to_distribution_f1 }}
      </div>
      <div>
        {{ $t('profit') }} : {{ row.item.profit }}
      </div>

      <b class="w-100 mb-0 mt-1">{{ $t('secondForm') }}:</b>
      <div>
        {{ $t('price') }} {{ $t('secondForm') }} : {{ row.item.price_form1 }}
      </div>
      <div>
        {{ $t('total') }} {{ $t('secondForm') }} : {{ row.item.sum_to_distribution_f2 }}
      </div>
      <div>
        {{ $t('profit') }} : {{ row.item.profit }}
      </div>
    </div>
  </b-card>
</template>

<script>
import { hideDetailed } from '@/mixins/main'

export default {
  name: 'ReportFinanceInfo',
  props: {
    row: Object
  },
  data () {
    return {
      hideDetailed
    }
  },
  mounted () {
    this.transferToString('sum_to_distribution_f1')
    this.transferToString('sum_to_distribution_f2')
  },
  methods: {
    transferToString (distributionLabel) {
      let distributionSum = this.row.item[distributionLabel]
      let distribution = []
      for (let d in distributionSum) {
        let label = this.setLabelName(d)
        distribution.push([label, distributionSum[d]].join(': '))
      }
      this.row.item[distributionLabel] = distribution.join(', ')
    },
    setLabelName (prop) {
      switch (prop) {
        case 'to_td': return this.$i18n.t('toTD')
        case 'to_sqc': return this.$i18n.t('toSQC')
        case 'to_qd': return this.$i18n.t('toQD')
        case 'to_sc': return this.$i18n.t('toSC')
        case 'to_agent': return this.$i18n.t('toAgent')
        case 'to_mrc': return this.$i18n.t('toMRC')
        case 'to_medical': return this.$i18n.t('toMedical')
        case 'to_cec': return this.$i18n.t('toCEC')
        case 'to_portal': return this.$i18n.t('toPortal')
        case 'to_eti': return this.$i18n.t('toETI')
        case 'amount': return this.$i18n.t('all')
      }
    }
  }
}
</script>
