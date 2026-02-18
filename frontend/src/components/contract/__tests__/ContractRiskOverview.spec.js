import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'

import ContractRiskOverview from '../ContractRiskOverview.vue'

describe('ContractRiskOverview', () => {
  it('renders risk level, completeness and summary counters', () => {
    const wrapper = mount(ContractRiskOverview, {
      props: {
        analysisResult: {
          risk_level: '中风险',
          completeness: 75,
          risk_summary: {
            高风险: 1,
            中风险: 2,
            需特别关注: 3
          }
        },
        foundElementsCount: 6,
        riskColor: '#E6A23C'
      },
      global: {
        stubs: {
          elIcon: true,
          WarnTriangleFilled: true,
          Warning: true,
          InfoFilled: true,
          Document: true
        }
      }
    })

    expect(wrapper.text()).toContain('中风险')
    expect(wrapper.text()).toContain('75%')
    expect(wrapper.text()).toContain('高风险')
    expect(wrapper.text()).toContain('中风险')
    expect(wrapper.text()).toContain('需关注')
    expect(wrapper.text()).toContain('已识别要素')
  })
})
