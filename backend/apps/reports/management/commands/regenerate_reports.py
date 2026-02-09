"""
重新生成报告管理命令
"""
from django.core.management.base import BaseCommand
from apps.executions.models import Execution
from apps.reports.models import Report
from apps.reports.generators import ReportGenerator
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '重新生成所有报告（包含建议功能）'

    def add_arguments(self, parser):
        parser.add_argument(
            '--execution-id',
            type=int,
            help='只重新生成指定执行ID的报告',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制重新生成所有报告（即使已存在）',
        )

    def handle(self, *args, **options):
        execution_id = options.get('execution_id')
        force = options.get('force', False)

        if execution_id:
            # 重新生成单个报告
            try:
                execution = Execution.objects.get(id=execution_id)
                self._regenerate_report(execution)
            except Execution.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'执行记录 ID {execution_id} 不存在'))
        else:
            # 重新生成所有报告
            if force:
                # 删除所有现有报告
                report_count = Report.objects.count()
                Report.objects.all().delete()
                self.stdout.write(self.style.WARNING(f'已删除 {report_count} 个旧报告'))

            # 重新生成所有已完成的执行记录的报告
            executions = Execution.objects.filter(
                status__in=['completed', 'failed', 'stopped']
            )

            total = executions.count()
            self.stdout.write(f'开始重新生成 {total} 个报告...')

            for i, execution in enumerate(executions, 1):
                self._regenerate_report(execution)
                if i % 10 == 0:
                    self.stdout.write(f'进度: {i}/{total}')

            self.stdout.write(self.style.SUCCESS(f'[SUCCESS] 完成！共生成 {total} 个报告'))

    def _regenerate_report(self, execution):
        """重新生成单个报告"""
        try:
            # 删除旧报告
            Report.objects.filter(execution=execution).delete()

            # 生成新报告
            generator = ReportGenerator(execution)
            report = generator.generate()

            # 检查是否包含建议数据
            has_suggestions = False
            if report.charts_data:
                failure_analysis = report.charts_data.get('failure_analysis', [])
                if failure_analysis:
                    for item in failure_analysis:
                        if 'suggestion' in item:
                            has_suggestions = True
                            break

            suggestion_text = "包含建议" if has_suggestions else "无建议"
            self.stdout.write(f'[OK] 报告已生成: 执行ID={execution.id}, 类型={execution.execution_type}, {suggestion_text}')

        except Exception as e:
            logger.error(f"生成报告失败 - execution_id={execution.id}: {e}", exc_info=True)
            self.stdout.write(self.style.ERROR(f'[FAIL] 生成报告失败: 执行ID={execution.id}, 错误={str(e)}'))
