/* A/B Audio Intake — native, bounded source transformations; no third-party code. */
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.ABAudioCore=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  function finite(n,min,max){return typeof n==='number'&&Number.isFinite(n)&&n>=min&&n<=max;}
  function clamp(n,min,max){return Math.max(min,Math.min(max,n));}
  function pitchRate(note,rootNote=60){
    if(!Number.isInteger(note)||!Number.isInteger(rootNote)||note<0||note>127||rootNote<0||rootNote>127)throw Error('Invalid MIDI pitch');
    return Math.pow(2,(note-rootNote)/12);
  }
  function summarizeAudio(buffer){
    if(!buffer||!finite(buffer.sampleRate,8000,384000)||!Number.isInteger(buffer.numberOfChannels)||buffer.numberOfChannels<1||buffer.numberOfChannels>8||!finite(buffer.duration,0.001,3600))throw Error('Invalid decoded audio');
    let sum=0,peak=0,count=0;
    const stride=Math.max(1,Math.floor(buffer.length/160000));
    for(let c=0;c<buffer.numberOfChannels;c++){
      const data=buffer.getChannelData(c);
      for(let i=0;i<data.length;i+=stride){const v=data[i];if(!Number.isFinite(v))continue;sum+=v*v;peak=Math.max(peak,Math.abs(v));count++;}
    }
    return {duration:buffer.duration,sampleRate:buffer.sampleRate,channels:buffer.numberOfChannels,peak:Math.min(1000,peak),rms:Math.sqrt(sum/Math.max(1,count))};
  }
  function envelope(buffer,bins=160){
    if(!buffer||!Number.isInteger(bins)||bins<8||bins>2048)throw Error('Invalid waveform request');
    const data=buffer.getChannelData(0), result=[];
    for(let b=0;b<bins;b++){
      const lo=Math.floor(data.length*b/bins), hi=Math.max(lo+1,Math.floor(data.length*(b+1)/bins));
      let min=1,max=-1;const skip=Math.max(1,Math.floor((hi-lo)/300));
      for(let i=lo;i<hi;i+=skip){const v=data[i];if(Number.isFinite(v)){min=Math.min(min,v);max=Math.max(max,v);}}
      result.push([clamp(min,-1,1),clamp(max,-1,1)]);
    }
    return result;
  }
  function encodeWav(buffer,startSec,endSec){
    if(!buffer||!finite(buffer.sampleRate,8000,384000)||!Number.isInteger(buffer.numberOfChannels)||buffer.numberOfChannels<1)throw Error('Bad audio');
    const channels=Math.min(2,buffer.numberOfChannels);
    if(!finite(startSec,0,buffer.duration)||!finite(endSec,startSec+0.01,buffer.duration+1/buffer.sampleRate))throw Error('Invalid slice');
    const start=Math.floor(startSec*buffer.sampleRate), end=Math.min(buffer.length,Math.ceil(endSec*buffer.sampleRate));
    const frames=end-start;
    if(frames<80||frames>buffer.sampleRate*45)throw Error('A WAV slice must be 0.01–45 seconds');
    const bytes=44+frames*channels*2;
    const array=new ArrayBuffer(bytes),v=new DataView(array);
    function str(off,s){for(let i=0;i<s.length;i++)v.setUint8(off+i,s.charCodeAt(i));}
    str(0,'RIFF');v.setUint32(4,bytes-8,true);str(8,'WAVE');str(12,'fmt ');
    v.setUint32(16,16,true);v.setUint16(20,1,true);v.setUint16(22,channels,true);
    v.setUint32(24,buffer.sampleRate,true);v.setUint32(28,buffer.sampleRate*channels*2,true);
    v.setUint16(32,channels*2,true);v.setUint16(34,16,true);str(36,'data');v.setUint32(40,bytes-44,true);
    const sources=Array.from({length:channels},(_,c)=>buffer.getChannelData(c));
    let p=44;
    for(let i=start;i<end;i++)for(let c=0;c<channels;c++){
      const x=clamp(Number.isFinite(sources[c][i])?sources[c][i]:0,-1,1);
      v.setInt16(p,x<0?Math.round(x*32768):Math.round(x*32767),true);p+=2;
    }
    return array;
  }
  function parseMidi(input){
    const a=input instanceof Uint8Array?input:new Uint8Array(input);
    if(a.length<14||a.length>5_000_000)throw Error('MIDI size outside bounds');
    let p=0;
    function need(n){if(p+n>a.length)throw Error('Truncated MIDI');}
    function byte(){need(1);return a[p++];}
    function word(){return(byte()<<8)|byte();}
    function long(){return(byte()*0x1000000+byte()*0x10000+byte()*0x100+byte());}
    function tag(){need(4);let s='';for(let i=0;i<4;i++)s+=String.fromCharCode(byte());return s;}
    function vlq(end){let v=0;for(let i=0;i<4;i++){if(p>=end)throw Error('Truncated MIDI variable integer');let b=byte();v=(v<<7)|(b&127);if(!(b&128))return v;}throw Error('Oversized MIDI variable integer');}
    if(tag()!=='MThd')throw Error('Not a MIDI file');
    const headerLength=long();if(headerLength<6||headerLength>1024)throw Error('Bad MIDI header');
    const format=word(), tracks=word(),division=word();
    if(format>1||tracks<1||tracks>64||!(division&0x7fff)||(division&0x8000))throw Error('Unsupported MIDI format or timing');
    p=8+headerLength;need(0); const raw=[],tempos=[{tick:0,us:500000}];let eventCount=0;
    for(let t=0;t<tracks;t++){
      if(tag()!=='MTrk')throw Error('Expected MIDI track');
      const size=long(), end=p+size;if(end>a.length)throw Error('Truncated MIDI track');
      let tick=0,status=0;const held=new Map();
      while(p<end){
        tick+=vlq(end);if(tick>100_000_000)throw Error('MIDI time outside bounds');
        let code=byte();if(code<128){if(!status)throw Error('MIDI running status missing');p--;code=status;}
        else if(code<240)status=code; else if(code!==0xf0&&code!==0xf7&&code!==0xff)throw Error('Unsupported MIDI system event');
        if(code===255){const type=byte(),sz=vlq(end);if(p+sz>end)throw Error('Truncated MIDI metadata');
          if(type===0x51&&sz===3){const us=(a[p]<<16)|(a[p+1]<<8)|a[p+2];if(us>0&&us<10_000_000)tempos.push({tick,us});}
          p+=sz;status=0;continue;
        }
        if(code===0xf0||code===0xf7){const sz=vlq(end);if(p+sz>end)throw Error('Truncated SysEx');p+=sz;status=0;continue;}
        const mode=code&240,ch=code&15,n=byte(); const vel=(mode===0xc0||mode===0xd0)?0:byte();
        if(n>127||vel>127)throw Error('Bad MIDI data');
        if(mode===0x90&&vel>0){const key=ch+':'+n, stack=held.get(key)||[];stack.push({tick,n,vel,ch,t});held.set(key,stack);}
        else if(mode===0x80||(mode===0x90&&vel===0)){
          const key=ch+':'+n, stack=held.get(key);
          if(stack&&stack.length){const first=stack.shift();if(tick>first.tick)raw.push({...first,endTick:tick});}
        }
        eventCount++;if(eventCount>100000)throw Error('MIDI event limit exceeded');
      }
      if(p!==end)throw Error('Track boundary mismatch');
    }
    tempos.sort((a,b)=>a.tick-b.tick);const timeline=[];let lastTick=0,micros=0,old=500000;
    for(const e of tempos){if(e.tick<lastTick)continue;micros+=(e.tick-lastTick)*old/division; timeline.push({tick:e.tick,micros,us:e.us});lastTick=e.tick;old=e.us;}
    function milliseconds(tick){let lo=0,hi=timeline.length-1;while(lo<hi){let mid=Math.ceil((lo+hi)/2);if(timeline[mid].tick<=tick)lo=mid;else hi=mid-1;}const x=timeline[lo];return(x.micros+(tick-x.tick)*x.us/division)/1000;}
    const notes=raw.map(n=>({midi:n.n,startMs:Math.round(milliseconds(n.tick)),endMs:Math.round(milliseconds(n.endTick)),velocity:n.vel,channel:n.ch,track:n.t})).filter(n=>n.endMs>n.startMs).sort((a,b)=>a.startMs-b.startMs||a.track-b.track);
    return {format,tracks,ppqn:division,notes,tempoEvents:tempos.length-1,initialBpm:120,durationMs:notes.reduce((m,n)=>Math.max(m,n.endMs),0)};
  }
  return Object.freeze({finite,clamp,pitchRate,summarizeAudio,envelope,encodeWav,parseMidi});
});