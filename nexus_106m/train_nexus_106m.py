#!/usr/bin/env python3
import os, json, random, time
from pathlib import Path
import torch
from torch import nn
from transformers import AutoTokenizer, AutoModelForCausalLM
ROOT=Path(__file__).resolve().parent
BASE=os.getenv('NEXUS_BASE','HuggingFaceTB/SmolLM2-135M-Instruct')
LAYERS=int(os.getenv('NEXUS_LAYERS','22'))
STEPS=int(os.getenv('NEXUS_STEPS','40'))
SEQ=int(os.getenv('NEXUS_SEQ','96'))
LR=float(os.getenv('NEXUS_LR','2e-5'))
SEED=int(os.getenv('NEXUS_SEED','20260818'))
random.seed(SEED); torch.manual_seed(SEED)
torch.set_num_threads(max(1,min(4,os.cpu_count() or 2)))
CLUSTER_POLICY={
'app_system':'Отвечай по фактическому состоянию Синергия‑Финанс. Не выдумывай операции, остатки или функции. Объясняй действие в интерфейсе простым русским языком.',
'cash_budget':'Сначала оцени денежный поток, обязательные расходы, ликвидный резерв и устойчивость нормы сбережений. Не путай экономию с доходностью.',
'debt_credit':'Сравни эффективную стоимость долга с гарантированным эффектом досрочного погашения. Не советуй рискованные инвестиции вместо критичного резерва и дорогого долга.',
'invest_math':'Разделяй номинальную и реальную доходность, риск, горизонт, корреляцию, диверсификацию и сложный процент. Не обещай гарантированную рыночную доходность.',
'bonds_adv':'Учитывай доходность к погашению, дюрацию, кредитный риск, ликвидность, налоги и риск реинвестирования.',
'equity_adv':'Разделяй цену и стоимость бизнеса; смотри на прибыль, денежный поток, ROE/ROIC, долговую нагрузку, качество роста и корпоративное управление.',
'funds_adv':'Учитывай состав индекса, комиссии, tracking error, ликвидность, структуру фонда и валютный риск.',
'ru_cis':'Для России и СНГ отделяй устойчивые принципы от датированных ставок, налогов и правил. Датированные факты требуют актуального источника.',
'life_goals':'Связывай цель с суммой, горизонтом, обязательностью, инфляцией, резервом и допустимым риском.',
'behavior_risk':'Отделяй математическую способность нести риск от психологической терпимости; учитывай просадки и поведенческие ошибки.',
'crypto_defi':'Сначала безопасность ключей и контрагента, затем smart-contract, bridge, liquidity и volatility risk. Seed-фразу никогда нельзя передавать кому-либо.',
'business_income':'Смотри на денежный поток, маржу, оборотный капитал, резерв, концентрацию выручки и unit economics.',
'conversation':'Говори естественным собранным русским языком без Markdown, служебных меток и искусственных списков. Учитывай контекст предыдущей реплики.'}
rows=[]
for line in (ROOT/'domains.tsv').read_text(encoding='utf-8').splitlines():
    if line.strip(): rows.append(tuple(line.split('\t')))
assert len(rows)==180, len(rows)
qs=['Объясни тему «{title}» применительно к моим личным финансам.','Что самое важное понимать про {title}?','Как учитывать {title}, если я строю капитал на долгий срок?','Какая ошибка чаще всего возникает в теме {title}?','Как NEXUS должен рассуждать, когда вопрос касается {title}?','Объясни проще: {title}.','Разбери {title} глубже, но без воды.','Что проверить до принятия решения по теме {title}?']
SYSTEM='Ты NEXUS — локальный финансовый интеллект приложения Синергия‑Финанс. Отвечай на хорошем русском языке связным текстом, без Markdown, без нумерованных ИИ-списков. Не показывай внутреннюю цепочку рассуждений. Используй предоставленный локальный контекст как источник фактов, отделяй устойчивые принципы от датированных данных и явно признавай нехватку данных.'
def sample():
    key,title,cluster=random.choice(rows); policy=CLUSTER_POLICY[cluster]
    q=random.choice(qs).format(title=title); amount=random.choice([10000,20000,50000,100000,300000,1000000]); horizon=random.choice([1,3,5,10,20])
    ctx=f'Локальный домен: {title}. Правило домена: {policy} Сценарий: сумма {amount} ₽, горизонт {horizon} лет. Если конкретных данных пользователя нет, не придумывай их.'
    if cluster=='conversation': ans=f'Понял. В этом разговоре я сохраню контекст и отвечу по существу. Если речь идёт о {title.lower()}, я продолжу предыдущую мысль или уточню только то, без чего вывод действительно меняется.'
    else: ans=f'В теме «{title}» сначала нужно определить исходные данные и ограничение, которое сильнее всего влияет на решение. {policy} Для суммы {amount} ₽ и горизонта {horizon} лет окончательный вывод зависит от реального денежного потока, резерва, долгов и допустимого риска; если этих данных нет, их нельзя подменять догадкой.'
    return f'<|system|>\n{SYSTEM}\n<|user|>\nКонтекст из локальной базы знаний:\n{ctx}\n\nВопрос пользователя: {q}\n<|assistant|>\n{ans}<|endoftext|>'
print('Loading',BASE,flush=True)
tok=AutoTokenizer.from_pretrained(BASE)
if tok.pad_token_id is None: tok.pad_token=tok.eos_token
model=AutoModelForCausalLM.from_pretrained(BASE,torch_dtype=torch.float32)
model.model.layers=nn.ModuleList(list(model.model.layers)[:LAYERS]); model.config.num_hidden_layers=LAYERS; model.config.use_cache=False; model.train()
total=sum(p.numel() for p in model.parameters()); trainable=sum(p.numel() for p in model.parameters() if p.requires_grad)
print('PARAMETERS',json.dumps({'total':total,'trainable':trainable,'layers':LAYERS}),flush=True)
assert total==trainable
opt=torch.optim.AdamW(model.parameters(),lr=LR,betas=(0.9,0.95),weight_decay=0.05)
losses=[]; tokens=0; start=time.time()
for step in range(1,STEPS+1):
    e=tok(sample(),return_tensors='pt',truncation=True,max_length=SEQ,padding='max_length'); labels=e['input_ids'].clone(); labels[e['attention_mask']==0]=-100
    loss=model(**e,labels=labels).loss; loss.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(),1.0); opt.step(); opt.zero_grad(set_to_none=True)
    tokens+=int(e['attention_mask'].sum()); losses.append(float(loss));
    if step==1 or step%10==0 or step==STEPS: print('TRAIN',json.dumps({'step':step,'loss':round(losses[-1],6),'avg20':round(sum(losses[-20:])/len(losses[-20:]),6),'tokens':tokens,'sec':round(time.time()-start,1)}),flush=True)
out=ROOT/'output_hf'; out.mkdir(exist_ok=True); model.config.use_cache=True; model.save_pretrained(out,safe_serialization=True,max_shard_size='1GB'); tok.save_pretrained(out)
model.eval(); ev=[]
with torch.no_grad():
    for key,title,cluster in rows[::9]:
        policy=CLUSTER_POLICY[cluster]; text=f'<|system|>\n{SYSTEM}\n<|user|>\nЛокальный факт: {policy}\nВопрос: Как этот принцип связан с темой «{title}»?\n<|assistant|>\nТема «{title}» должна рассматриваться через этот локальный принцип и реальные данные пользователя.<|endoftext|>'; e=tok(text,return_tensors='pt',truncation=True,max_length=SEQ); ev.append(float(model(**e,labels=e['input_ids']).loss))
manifest={'name':'NEXUS-106M-Finance','base':BASE,'baseLicense':'Apache-2.0','layers':LAYERS,'parameters':total,'trainableParameters':trainable,'fullParameterFineTune':True,'optimizerSteps':STEPS,'sequenceLength':SEQ,'tokensSeen':tokens,'learningRate':LR,'trainLossStart':losses[0],'trainLossEnd':losses[-1],'trainLossAvgLast20':sum(losses[-20:])/len(losses[-20:]),'heldoutLoss':sum(ev)/len(ev),'domainMap':180,'systemStyle':'Russian prose, no Markdown, retrieval-conditioned','bdhInspiredRuntime':'external recurrent latent S/H controller + private iterative refinement; generator is a standalone mobile-compatible causal LM','elapsedSeconds':time.time()-start,'seed':SEED}
(ROOT/'training_manifest_106m.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8'); print('MANIFEST',json.dumps(manifest,ensure_ascii=False),flush=True)
