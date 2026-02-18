import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'

import RequirementsScoreOverview from '../RequirementsScoreOverview.vue'

describe('RequirementsScoreOverview', () => {
  it('shows score and issue counters', () => {
    const wrapper = mount(RequirementsScoreOverview, {
      props: {
        reviewResult: {
          completeness_score: 88,
          error_count: 1,
          warning_count: 2,
          info_count: 3,
          field_count: 4
        },
        categoryName: '服务器',
        subtypeName: 'AI服务器',
        scoreColor: '#67C23A',
        scoreStatus: '优秀'
      },
      global: {
        stubs: {
          elIcon: true,
          elTag: true,
          CircleClose: true,
          Warning: true,
          InfoFilled: true,
          Document: true
        }
      }
    })

    expect(wrapper.text()).toContain('88')
    expect(wrapper.text()).toContain('优秀')
    expect(wrapper.text()).toContain('错误')
    expect(wrapper.text()).toContain('警告')
    expect(wrapper.text()).toContain('提示')
    expect(wrapper.text()).toContain('提取字段')
  })
})
